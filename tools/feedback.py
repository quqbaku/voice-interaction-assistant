"""反馈工具"""
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Optional

from .base import BaseTool

logger = logging.getLogger(__name__)


class FeedbackTool(BaseTool):
    """用户反馈工具"""

    name = "user_feedback"
    description = "向用户反馈信息，包括语音播报、通知提醒等"

    def __init__(self, tts_engine: str = "pyttsx3"):
        self.tts_engine = tts_engine
        self._init_tts()

    def _init_tts(self):
        try:
            if self.tts_engine == "pyttsx3":
                import pyttsx3
                self._tts = pyttsx3.init()
            else:
                self._tts = None
        except Exception as e:
            logger.warning(f"TTS 初始化失败: {e}")
            self._tts = None

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["speak", "notify", "remind"],
                    "description": "反馈操作"
                },
                "text": {"type": "string", "description": "播报文本"},
                "title": {"type": "string", "description": "通知标题"},
                "message": {"type": "string", "description": "通知内容"},
                "seconds": {"type": "integer", "description": "延迟秒数"},
            },
            "required": ["action"]
        }

    def execute(self, action: str, text: str = None, title: str = None, message: str = None, seconds: int = None) -> str:
        try:
            if action == "speak":
                return self._speak(text or "")
            elif action == "notify":
                return self._notify(title or "提示", message or "")
            elif action == "remind":
                return self._remind(message or "", seconds or 60)
            return f"未知操作: {action}"
        except Exception as e:
            logger.error(f"FeedbackTool 执行失败: {e}")
            return f"反馈失败: {e}"

    def _speak(self, text: str) -> str:
        if not text:
            return "请提供要播报的文本"
        if self._tts:
            self._tts.say(text)
            self._tts.runAndWait()
        return f"已播报: {text}"

    def _notify(self, title: str, message: str) -> str:
        if not message:
            return "请提供通知内容"
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
            return f"已发送通知: {title}"
        except ImportError:
            # 降级方案
            subprocess.run(["powershell", "-Command", f'(New-Object -ComObject WScript.Shell).Popup("{message}", 5, "{title}", 0)'])
            return f"已发送通知: {title}"

    def _remind(self, message: str, seconds: int) -> str:
        if not message:
            return "请提供提醒内容"

        def delayed_notify():
            import time
            time.sleep(seconds)
            self._notify("定时提醒", message)

        thread = threading.Thread(target=delayed_notify, daemon=True)
        thread.start()
        return f"已设置 {seconds} 秒后提醒: {message}"
