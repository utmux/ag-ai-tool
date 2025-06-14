# ag_cli/renderer.py (Corrected)

from rich.console import Console
from rich.markdown import Markdown

console = Console()

def render_markdown(text: str):
    """将完整的 Markdown 文本渲染到控制台。"""
    markdown = Markdown(text, code_theme="monokai", inline_code_theme="monokai")
    console.print(markdown)

def render_stream(stream_generator):
    """实时渲染来自 API 的流式响应。"""
    full_response = ""
    for chunk in stream_generator:
        if chunk:
            full_response += chunk
            # --- 【核心修改】 ---
            # 去掉了 rich.print() 不支持的 flush=True 参数
            console.print(chunk, end="")
    
    # 在所有内容都打印完毕后，打印一个换行符，使终端提示符另起一行
    console.print() 
    return full_response