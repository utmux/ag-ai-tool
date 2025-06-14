# ag_cli/config.py (Final Simplified Version)

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

CONFIG_DIR = Path.home() / ".config" / "ag"
CONFIG_FILE = CONFIG_DIR / "config.json"

# --- 【核心修改】 ---
# 更新默认配置模板，以反映最终的、极简的架构。
# 不再有 'type', 'endpoint', 'headers' 等字段。
# 注释中强调 api_key 不需要 "Bearer " 前缀。
DEFAULT_CONFIG = {
    "default_model": "gpt-4o",
    "current_provider": "openai_official",
    "providers": {
        "openai_official": {
            # 注：openai 库会自动处理认证，请直接填写密钥
            "api_key": "sk-YOUR_OFFICIAL_OPENAI_KEY_HERE",
            "api_base": "https://api.openai.com/v1",
            "models": ["gpt-4o", "gpt-3.5-turbo"]
        },
        "ctyun_wishub": {
            # 注：同样直接填写密钥，不要加 "Bearer "
            "api_key": "YOUR_CTYUN_APP_KEY_HERE",
            "api_base": "https://wishub-x1.ctyun.cn/v1",
            "models": ["YOUR_CTYUN_MODEL_ID_HERE"],
            "system_prompt": "你是一个Linux命令行专家，请用中文回答，并尽可能提供命令示例。", 
            "extra_payload": {
                "temperature": 1.0,
                "max_tokens": 4096
            }
        }
    }
}

def ensure_config_exists():
    """确保配置文件和目录存在，如果不存在则使用最新的模板创建。"""
    if not CONFIG_DIR.exists():
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"Configuration file created at: {CONFIG_FILE}")
        print("Please edit it to add your API keys.")


def load_config() -> Dict[str, Any]:
    """加载配置文件。"""
    ensure_config_exists()
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Configuration file at {CONFIG_FILE} is corrupted. Please fix or delete it.")
        sys.exit(1)


def save_config(data: Dict[str, Any]):
    """保存配置。"""
    ensure_config_exists()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_default_model() -> Optional[str]:
    """获取配置中设置的默认模型。"""
    config = load_config()
    return config.get("default_model")


def find_provider_for_model(model_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """根据模型名称查找对应的供应商。"""
    config = load_config()
    # providers 键可能不存在于一个空的或损坏的 config 中
    for name, provider_info in config.get("providers", {}).items():
        if model_name in provider_info.get("models", []):
            return name, provider_info
    return None


def get_current_provider_info() -> Tuple[str, Dict[str, Any]]:
    """获取当前激活的供应商名称和配置。"""
    config = load_config()
    providers = config.get("providers", {})
    provider_name = config.get("current_provider")
    if not provider_name or provider_name not in providers:
        print(f"Error: Current provider '{provider_name}' is not defined or valid in config.json.")
        sys.exit(1)
    return provider_name, providers[provider_name]