"""应用管理工具"""
import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class AppTool(BaseTool):
    """应用管理工具"""

    name = "app_manager"
    description = "管理应用程序，包括打开、关闭、查询已安装应用"

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.app_map = self._load_app_map()
        self.installed_apps = None

    def _load_app_map(self) -> dict:
        """加载应用映射"""
        map_path = self.config.get("app", {}).get("app_map_path", "config/app_map.json")
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载 app_map 失败: {e}")
            return {}

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["scan", "launch", "close", "check", "list"],
                    "description": "操作类型"
                },
                "name": {"type": "string", "description": "应用名称或关键词"},
            },
            "required": ["action"]
        }

    def execute(self, action: str, name: str = None) -> str:
        try:
            if action == "scan":
                return self._scan_apps()
            elif action == "launch":
                return self._launch_app(name)
            elif action == "close":
                return self._close_app(name)
            elif action == "check":
                return self._check_app(name)
            elif action == "list":
                return self._list_apps()
            return f"未知操作: {action}"
        except Exception as e:
            logger.error(f"AppTool 执行失败: {e}")
            return f"操作失败: {e}"

    def _scan_apps(self) -> str:
        """扫描已安装应用"""
        if self.installed_apps:
            return f"已扫描到 {len(self.installed_apps)} 个应用"

        apps = []
        scan_paths = self.config.get("app", {}).get("scan_paths", [])

        for base_path in scan_paths:
            base_path = os.path.expandvars(base_path)
            if not os.path.exists(base_path):
                continue
            for root, _, files in os.walk(base_path):
                for f in files:
                    if f.endswith((".exe", ".lnk")) and not f.startswith("unins"):
                        apps.append(f)

        # 去重
        seen = set()
        unique_apps = []
        for app in apps:
            name = os.path.splitext(app)[0].lower()
            if name not in seen:
                seen.add(name)
                unique_apps.append(app)

        self.installed_apps = unique_apps
        return f"扫描完成，共发现 {len(unique_apps)} 个应用"

    def _launch_app(self, name: str) -> str:
        if not name:
            return "请指定应用名称"

        # 优先从 app_map 查找
        for key, path in self.app_map.items():
            if key.lower() in name.lower() or name.lower() in key.lower():
                try:
                    subprocess.Popen(path, shell=True)
                    return f"已打开 {key}"
                except Exception as e:
                    return f"打开失败: {e}"

        # 尝试直接启动
        try:
            subprocess.Popen(name, shell=True)
            return f"已打开 {name}"
        except:
            return f"未找到应用: {name}"

    def _close_app(self, name: str) -> str:
        if not name:
            return "请指定应用名称"

        # 杀掉进程
        try:
            subprocess.run(["taskkill", "/IM", f"{name}.exe", "/F"], check=True)
            return f"已关闭 {name}"
        except:
            return f"关闭失败或应用不存在: {name}"

    def _check_app(self, name: str) -> str:
        if not name:
            return "请指定应用名称"

        # 检查 app_map
        for key, path in self.app_map.items():
            if key.lower() in name.lower():
                if os.path.exists(path):
                    return f"{key} 已安装"
                return f"{key} 配置存在但文件未找到"

        # 检查进程
        try:
            result = subprocess.run(
                ["tasklist"], capture_output=True, text=True
            )
            if name.lower() in result.stdout.lower():
                return f"{name} 正在运行"
        except:
            pass

        return f"未找到 {name}"

    def _list_apps(self) -> str:
        """列出已注册的应用"""
        if not self.app_map:
            return "没有已注册的应用"
        lines = [f"已注册应用 ({len(self.app_map)} 个):"]
        for name in self.app_map:
            lines.append(f"  - {name}")
        return "\n".join(lines)
