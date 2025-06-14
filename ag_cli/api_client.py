# ag_cli/api_client.py (Ultimate Simplification)

import re
from openai import OpenAI
from typing import List, Dict, Any, Generator

from rich.console import Console
from .config import find_provider_for_model, get_current_provider_info

console = Console()

def clean_content(content: str) -> str:
    """从内容中移除 <think>...</think> 标签块。"""
    # re.DOTALL 允许 '.' 匹配包括换行在内的任何字符
    if content:
        return re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL).strip()
    return ""

def get_completion_stream(messages: List, model_name: str | None) -> Generator[str, None, None]:
    """
    终极版通用处理器。
    只使用 openai 库来处理所有兼容的 API。
    """
    provider_name, provider_info = None, None
    
    # 1. 查找要使用的供应商和模型
    if model_name:
        result = find_provider_for_model(model_name)
        if not result:
            console.print(f"[bold red]Error: Model '{model_name}' not found.[/bold red]"); return
        provider_name, provider_info = result
    else:
        try:
            provider_name, provider_info = get_current_provider_info()
            model_name = provider_info["models"][0]
        except Exception as e:
            console.print(f"[bold red]Error: No default model/provider: {e}[/bold red]"); return

    console.print(f"[grey50]Using model '{model_name}' from provider '{provider_name}'...[/grey50]")
    
    # 2. 初始化 OpenAI 客户端，并指向正确的 API 地址
    try:
        client = OpenAI(
            # 注意：api_key 直接传递，库会自动处理 'Bearer' 认证
            api_key=provider_info["api_key"],
            base_url=provider_info["api_base"],
        )

        # 3. 准备请求参数，并智能合并 extra_payload
        params = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }
        if "extra_payload" in provider_info:
            params.update(provider_info["extra_payload"])

        # 4. 发起流式请求
        stream = client.chat.completions.create(**params)

        # 5. 迭代处理并返回内容
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            yield content

    except Exception as e:
        console.print(f"\n[bold red]An API error occurred: {e}[/bold red]")