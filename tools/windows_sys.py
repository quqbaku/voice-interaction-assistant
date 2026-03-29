"""Windows 系统控制工具"""
import logging
import subprocess
from pathlib import Path

from .base import BaseTool

logger = logging.getLogger(__name__)


class SystemTool(BaseTool):
    """Windows 系统控制工具"""

    name = "system_control"
    description = "控制系统设置，包括音量、屏幕、电源管理等"

    PANELS = {
        "设置": "ms-settings:",
        "控制面板": "control panel",
        "任务管理器": "taskmgr",
        "网络": "ms-settings:network",
        "蓝牙": "ms-settings:bluetooth",
        "声音": "ms-settings:sound",
        "显示": "ms-settings:display",
        "个性化": "ms-settings:personalization",
        "应用": "ms-settings:appsfeatures",
        "任务栏": "ms-settings:taskbar",
        "电源": "ms-settings:powersleep",
        "投影": "ms-settings:project",
        "截图": "ms-screenclip",
        "回收站": "shell:RecycleBinFolder",
    }

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["set_volume", "get_volume", "mute", "lock", "shutdown", "restart", "sleep", "screenshot", "open_panel", "empty_recycle_bin"],
                    "description": "操作类型"
                },
                "level": {"type": "integer", "minimum": 0, "maximum": 100, "description": "音量级别 (0-100)"},
                "panel": {"type": "string", "description": "设置面板名称"},
            },
            "required": ["action"]
        }

    def execute(self, action: str, level: int = None, panel: str = None) -> str:
        try:
            if action == "set_volume":
                return self._set_volume(level or 50)
            elif action == "get_volume":
                return self._get_volume()
            elif action == "mute":
                return self._mute()
            elif action == "lock":
                return self._lock_screen()
            elif action == "shutdown":
                return self._shutdown()
            elif action == "restart":
                return self._restart()
            elif action == "sleep":
                return self._sleep()
            elif action == "screenshot":
                return self._screenshot()
            elif action == "open_panel":
                return self._open_panel(panel or "设置")
            elif action == "empty_recycle_bin":
                return self._empty_recycle_bin()
            return f"未知操作: {action}"
        except Exception as e:
            logger.error(f"SystemTool 执行失败: {e}")
            return f"操作失败: {e}"

    def _set_volume(self, level: int) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"音量已设置为 {level}%"
        except ImportError:
            # 降级方案
            subprocess.run(["powershell", "-Command", f"(Get-AudioDevice -Playback -Volume {level})"], capture_output=True)
            return f"音量已设置为 {level}%"

    def _get_volume(self) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            level = int(volume.GetMasterVolumeLevelScalar() * 100)
            return f"当前音量: {level}%"
        except:
            return "无法获取音量"

    def _mute(self) -> str:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1 if volume.GetMute() == 0 else 0, None)
            state = "已静音" if volume.GetMute() else "已取消静音"
            return state
        except:
            return "静音切换失败"

    def _lock_screen(self) -> str:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        return "屏幕已锁定"

    def _shutdown(self) -> str:
        subprocess.run(["shutdown", "/s", "/t", "30"], check=True)
        return "系统将在 30 秒后关机"

    def _restart(self) -> str:
        subprocess.run(["shutdown", "/r", "/t", "30"], check=True)
        return "系统将在 30 秒后重启"

    def _sleep(self) -> str:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], check=True)
        return "系统已进入睡眠模式"

    def _screenshot(self) -> str:
        import pyautogui
        from datetime import datetime
        path = Path.home() / "Pictures" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(str(path))
        return f"截图已保存到 {path}"

    def _open_panel(self, panel: str) -> str:
        panel_uri = self.PANELS.get(panel, f"ms-settings:{panel}")
        try:
            subprocess.run(["start", "", panel_uri], shell=True, check=True)
            return f"已打开 {panel}"
        except:
            return f"无法打开 {panel}"

    def _empty_recycle_bin(self) -> str:
        import winshell
        winshell.delete_file_contents(winshell.recycle_bin(), allow_undo=False)
        return "回收站已清空"
