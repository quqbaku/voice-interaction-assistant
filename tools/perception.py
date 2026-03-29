"""系统感知工具"""
import logging
import subprocess
from typing import Optional

import psutil

from .base import BaseTool

logger = logging.getLogger(__name__)


class PerceptionTool(BaseTool):
    """系统感知工具"""

    name = "system_perception"
    description = "感知系统状态，包括焦点窗口、运行进程、屏幕内容等"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["focused_window", "running_processes", "screenshot", "volume"],
                    "description": "感知操作"
                },
            },
            "required": ["action"]
        }

    def execute(self, action: str) -> str:
        try:
            if action == "focused_window":
                return self._get_focused_window()
            elif action == "running_processes":
                return self._get_running_processes()
            elif action == "screenshot":
                return self._take_screenshot()
            elif action == "volume":
                return self._get_volume()
            return f"未知操作: {action}"
        except Exception as e:
            logger.error(f"PerceptionTool 执行失败: {e}")
            return f"感知失败: {e}"

    def _get_focused_window(self) -> str:
        """获取焦点窗口"""
        try:
            import win32gui
            import win32process
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return f"窗口: {title} (PID: {pid})"
        except ImportError:
            return "win32gui 未安装"
        except:
            return "无法获取焦点窗口"

    def _get_running_processes(self) -> str:
        """获取运行中的进程"""
        processes = []
        for p in psutil.process_iter(['name']):
            try:
                processes.append(p.info['name'])
            except:
                pass
        unique = list(dict.fromkeys(processes))[:20]
        return f"运行中的进程 (前20): {', '.join(unique)}"

    def _take_screenshot(self) -> str:
        """截图"""
        import pyautogui
        from datetime import datetime
        from pathlib import Path
        path = Path.home() / "Pictures" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(str(path))
        return f"截图已保存: {path}"

    def _get_volume(self) -> str:
        """获取音量"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            level = int(volume.GetMasterVolumeLevelScalar() * 100)
            muted = volume.GetMute()
            return f"音量: {level}% {'(已静音)' if muted else ''}"
        except:
            return "无法获取音量"
