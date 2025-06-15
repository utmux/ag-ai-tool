#!/usr/bin/env python3
# ag_cli/cli.py (With @file path completion)

import sys
import click
from datetime import datetime
import glob  # <--- 新增导入 glob 模块，用于文件路径匹配
import os    # <--- 新增导入 os 模块，用于判断是否是目录

from . import config, session, processor, renderer, api_client

# --- 【新增】@file 路径的动态补全函数 ---

def complete_at_file(ctx, param, incomplete):
    """
    为 @file 语法提供文件和路径补全。
    """
    # 只在用户输入的词以 @ 开头时触发
    if not incomplete.startswith('@'):
        return []

    # 移除 '@' 符号，得到路径前缀
    path_prefix = incomplete[1:]
    
    completions = []
    # 使用 glob 查找匹配项，* 会匹配任何字符
    for match in glob.glob(path_prefix + '*'):
        # 如果匹配项是一个目录，我们在末尾添加一个斜杠
        if os.path.isdir(match):
            completions.append('@' + match + '/')
        else:
            completions.append('@' + match)
    
    return completions


# --- 【新增】之前为 agc 写的动态补全函数，也放在这里 ---

def complete_providers(ctx, param, incomplete):
    """为 provider-set 命令动态返回所有可用的 provider 名称。"""
    conf = config.load_config()
    provider_names = list(conf.get("providers", {}).keys())
    return [p for p in provider_names if p.startswith(incomplete)]

def complete_models(ctx, param, incomplete):
    """为 model-set-default 命令动态返回所有可用的 model 名称。"""
    conf = config.load_config()
    all_models = []
    for provider in conf.get("providers", {}).values():
        all_models.extend(provider.get("models", []))
    return [m for m in all_models if m.startswith(incomplete)]

# ==============================================================================
#  CLI 入口和命令定义
# ==============================================================================

@click.command(name="ag")
@click.option('-m', '--model', 'model_flag', default=None, help='Specify a model to use.')
@click.option('--new', is_flag=True, help='Start a new chat session.')
@click.option('-s', '--session-id', 'session_id_flag', default=None, help='Continue a specific session.')
# --- 【核心修改】 ---
# 将 complete_at_file 函数关联到 prompt_words 参数
@click.argument('prompt_words', nargs=-1, shell_complete=complete_at_file)
def main_ask(model_flag, new, session_id_flag, prompt_words):
    """Ask a question, start an interactive session, or process piped data."""
    # ... 函数体不变 ...
    prompt = " ".join(prompt_words)
    model_to_use = model_flag or config.get_default_model()
    session_id = "default"
    if new: session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    elif session_id_flag: session_id = session_id_flag
    
    session_manager = session.SessionManager(session_id)
    if not prompt and sys.stdin.isatty():
        renderer.console.print(f"[bold cyan]Starting interactive session: {session_id} (Ctrl+D to exit)[/bold cyan]")
        while True:
            try:
                user_input = input("You: ")
                if user_input.strip(): handle_prompt(user_input, None, session_manager, model_to_use)
            except EOFError: renderer.console.print("\n[bold cyan]Session ended.[/bold cyan]"); break
    else:
        piped_data = processor.get_piped_input()
        handle_prompt(prompt, piped_data, session_manager, model_to_use)

def handle_prompt(user_prompt, piped_data, session_manager, model):
    """通用处理函数"""
    # ... 函数体不变 ...
    final_content = processor.build_final_content(user_prompt, piped_data)
    session_manager.add_message("user", final_content)
    stream_generator = api_client.get_completion_stream(session_manager.get_history(), model)
    if stream_generator:
        renderer.console.print(f"[bold magenta]AG:[/bold magenta]")
        full_response = renderer.render_stream(stream_generator)
        cleaned_response = api_client.clean_content(full_response)
        session_manager.add_message("assistant", cleaned_response)
        session_manager.save()

@click.group(name="agc")
def main_config():
    """Manages ag's configuration (providers, models, etc.)."""
    pass

@main_config.command(name="provider-list")
def provider_list():
    """List all configured providers."""
    # ... 函数体不变 ...
    conf = config.load_config()
    current_provider = conf.get("current_provider")
    renderer.console.print("[bold]Available Providers:[/bold]")
    for name, info in conf.get("providers", {}).items():
        is_current = " (current)" if name == current_provider else ""
        default_model_indicator = ""
        if name == current_provider:
             default_model = conf.get('default_model', 'N/A')
             default_model_indicator = f" (default model: [yellow]{default_model}[/yellow])"
        system_prompt_indicator = ""
        if info.get("system_prompt"):
            system_prompt_indicator = f"\n   System Prompt: [italic green]\"{info['system_prompt'][:40]}...\"[/italic green]"
        models = ", ".join(info.get("models", ["N/A"]))
        renderer.console.print(f" - [cyan]{name}[/cyan]{is_current}{default_model_indicator}\n   Models: {models}{system_prompt_indicator}")

@main_config.command(name="provider-set")
@click.argument('name', shell_complete=complete_providers)
def provider_set(name):
    """Set the default API provider."""
    # ... 函数体不变 ...
    conf = config.load_config()
    if name not in conf["providers"]: renderer.console.print(f"[red]Error: Provider '{name}' not found.[/red]"); sys.exit(1)
    conf["current_provider"] = name
    if conf["providers"][name].get("models"):
        new_default_model = conf["providers"][name]["models"][0]
        conf["default_model"] = new_default_model
        renderer.console.print(f"Default model updated to '[cyan]{new_default_model}[/cyan]'.")
    config.save_config(conf)
    renderer.console.print(f"[bold green]Default provider set to '[cyan]{name}[/cyan]'.[/bold green]")

@main_config.command(name="model-set-default")
@click.argument('model_name', shell_complete=complete_models)
def model_set_default(model_name):
    """Sets a model as the default for all commands."""
    # ... 函数体不变 ...
    conf = config.load_config()
    provider_info = config.find_provider_for_model(model_name)
    if not provider_info: renderer.console.print(f"[red]Error: Model '{model_name}' not found.[/red]"); sys.exit(1)
    provider_name, _ = provider_info
    conf["default_model"] = model_name
    conf["current_provider"] = provider_name
    config.save_config(conf)
    renderer.console.print(f"[green]Success! Default model set to '[cyan]{model_name}[/cyan]'.[/green]")