# ag_cli/session.py
import json
import os
from pathlib import Path
from typing import List, Dict, Any

HISTORY_DIR = Path.home() / ".config" / "ag" / "history"

class SessionManager:
    """管理单个对话会话的历史记录。"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        if not HISTORY_DIR.exists():
            os.makedirs(HISTORY_DIR, exist_ok=True)
        self.filepath = HISTORY_DIR / f"{self.session_id}.json"
        self.history: List[Dict[str, Any]] = self.load()

    def load(self) -> List[Dict[str, Any]]:
        """从 JSON 文件加载会话历史。"""
        if self.filepath.exists():
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return [] # 如果文件损坏，则开始新会话
        return []

    def add_message(self, role: str, content: str):
        """向历史记录中添加一条新消息。"""
        self.history.append({"role": role, "content": content})

    def save(self):
        """将会话历史保存到 JSON 文件。"""
        with open(self.filepath, "w") as f:
            json.dump(self.history, f, indent=4)

    def get_history(self) -> List[Dict[str, Any]]:
        """获取当前会话历史。"""
        return self.history