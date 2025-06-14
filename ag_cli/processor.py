# ag_cli/processor.py
import re
import sys
from pathlib import Path

def get_piped_input() -> str | None:
    """如果存在，则从 stdin 读取管道输入。"""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None

def process_at_files(prompt: str) -> str:
    """在 prompt 中查找 @file 语法并替换为文件内容。"""
    def replace_match(match):
        filepath = Path(match.group(1))
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"[Error: File '{filepath}' not found]"
        except Exception as e:
            return f"[Error reading file '{filepath}': {e}]"

    return re.sub(r'@(\S+)', replace_match, prompt)

def build_final_content(user_prompt: str, piped_data: str | None) -> str:
    """构建最终发送给 API 的内容。"""
    processed_prompt = process_at_files(user_prompt)
    
    if piped_data:
        return f"CONTEXT FROM PIPE:\n---\n{piped_data}\n---\n\nUSER QUESTION:\n{processed_prompt}"
    
    return processed_prompt