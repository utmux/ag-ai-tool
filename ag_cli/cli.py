#!/usr/bin/env python3
# ag_cli/cli.py (With System Prompt Support)

import sys
import click
from datetime import datetime

from . import config, session, processor, renderer, api_client

# ==============================================================================
#  主入口和子命令 (这部分不变)
# ==============================================================================
@click.command(name="ag")
@click.option('-m', '--model', 'model_flag', default=None, help='Specify a model to use.')
@click.option('--new', is_flag=True, help='Start a new chat session.')
@click.option('-s', '--session-id', 'session_id_flag', default=None, help='Continue a specific session.')
@click.argument('prompt_words', nargs=-1)
def main_ask(model_flag, new, session_id_flag, prompt_words):
    """Ask a question, start an interactive session, or process piped data."""
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

# ==============================================================================
#  核心处理函数 (handle_prompt)
#  --- 【核心修改】 ---
# ==============================================================================
def handle_prompt(user_prompt, piped_data, session_manager, model):
    """
    通用处理函数
    【新功能】在会话开始时，自动添加 system_prompt。
    """
    # 1. 获取当前供应商的完整配置信息
    # 我们需要它来检查是否存在 system_prompt
    provider_name, provider_info = config.find_provider_for_model(model) or (None, None)
    if not provider_info:
        try:
            provider_name, provider_info = config.get_current_provider_info()
        except Exception as e:
            renderer.console.print(f"[bold red]{e}[/bold red]")
            return

    # 2. 检查并添加 System Prompt
    system_prompt = provider_info.get("system_prompt")
    # 只在会话历史为空（即新会话的第一条消息）时，才添加 system_prompt
    if system_prompt and not session_manager.get_history():
        session_manager.add_message("system", system_prompt)

    # 3. 正常处理用户输入和 API 请求 (后续逻辑不变)
    final_content = processor.build_final_content(user_prompt, piped_data)
    session_manager.add_message("user", final_content)
    
    stream_generator = api_client.get_completion_stream(session_manager.get_history(), model)
    
    if stream_generator:
        renderer.console.print(f"[bold magenta]AG:[/bold magenta]")
        full_response = renderer.render_stream(stream_generator)
        
        # 清理并保存最终结果
        cleaned_response = api_client.clean_content(full_response)
        session_manager.add_message("assistant", cleaned_response)
        session_manager.save()


# ==============================================================================
#  agc 的配置命令 (这部分不变)
# ==============================================================================
@click.group(name="agc")
def main_config():
    """Manages ag's configuration (providers, models, etc.)."""
    pass

@main_config.command(name="provider-list")
# ... provider-list 的代码 ...
def provider_list():
    """List all configured providers."""
    conf = config.load_config()
    current_provider = conf.get("current_provider")
    renderer.console.print("[bold]Available Providers:[/bold]")
    for name, info in conf.get("providers", {}).items():
        is_current = " (current)" if name == current_provider else ""
        default_model_indicator = ""
        if name == current_provider:
             default_model = conf.get('default_model', 'N/A')
             default_model_indicator = f" (default model: [yellow]{default_model}[/yellow])"
        # 同时显示 system_prompt (如果存在)
        system_prompt_indicator = ""
        if info.get("system_prompt"):
            system_prompt_indicator = f"\n   System Prompt: [italic green]\"{info['system_prompt'][:40]}...\"[/italic green]"
        models = ", ".join(info.get("models", ["N/A"]))
        renderer.console.print(f" - [cyan]{name}[/cyan]{is_current}{default_model_indicator}\n   Models: {models}{system_prompt_indicator}")


@main_config.command(name="provider-set")
# ... provider-set 的代码 ...
@click.argument('name')
def provider_set(name):
    """Set the default API provider."""
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
# ... model-set-default 的代码 ...
@click.argument('model_name')
def model_set_default(model_name):
    """Sets a model as the default for all commands."""
    conf = config.load_config()
    provider_info = config.find_provider_for_model(model_name)
    if not provider_info: renderer.console.print(f"[red]Error: Model '{model_name}' not found.[/red]"); sys.exit(1)
    provider_name, _ = provider_info
    conf["default_model"] = model_name
    conf["current_provider"] = provider_name
    config.save_config(conf)
    renderer.console.print(f"[green]Success! Default model set to '[cyan]{model_name}[/cyan]'.[/green]")