"""配置加载模块"""
import os
import json
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    if not os.path.exists(config_path):
        return _default_config()

    with open(config_path, "r", encoding="utf-8") as f:
        if str(config_path).endswith(".yaml") or str(config_path).endswith(".yml"):
            cfg = yaml.safe_load(f) or {}
        else:
            cfg = json.load(f) or {}

    # 替换环境变量占位符
    cfg = _expand_env_vars(cfg)
    return cfg


def _expand_env_vars(obj: Any) -> Any:
    """递归替换环境变量占位符 ${VAR}"""
    if isinstance(obj, str):
        if obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        return obj
    elif isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    return obj


def _default_config() -> dict:
    """默认配置"""
    return {
        "llm": {
            "default": "minimax",
            "providers": {
                "minimax": {
                    "api_key": "",
                    "model": "MiniMax-M2.7",
                    "base_url": "https://api.minimaxi.com/v1",
                    "temperature": 1.0,
                    "max_tokens": 4096,
                    "reasoning_split": True,
                },
                "openai": {"api_key": "", "model": "gpt-4o", "temperature": 0.7},
                "anthropic": {"api_key": "", "model": "claude-sonnet-4-20250514", "temperature": 0.7},
                "ollama": {"base_url": "http://localhost:11434/v1", "model": "llama3", "temperature": 0.7},
            },
        },
        "wake_words": ["你好小猪", "小助手"],
        "speech": {"engine": "google", "model_path": "models/sense_voice", "tts_engine": "pyttsx3"},
        "app": {"scan_paths": [], "app_map_path": "config/app_map.json"},
        "plugins": {"path": "plugins", "enabled": True},
        "logging": {"level": "INFO", "file": "assistant.log"},
        "features": {"enable_wake_word": False, "enable_asr_correction": True, "enable_douyin_control": True, "confirm_dangerous_actions": True},
    }
