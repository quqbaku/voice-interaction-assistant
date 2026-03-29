"""抖音自动化工具"""
import logging
import time
import pyautogui

from .base import BaseTool

logger = logging.getLogger(__name__)


class DouyinTool(BaseTool):
    """抖音键盘自动化工具"""

    name = "douyin_control"
    description = "控制抖音桌面版的各种操作"

    HOTKEYS = {
        "play": "space",
        "pause": "space",
        "like": "l",
        "unlike": "l",
        "follow": "f",
        "unfollow": "f",
        "comment": "i",
        "share": "s",
        "favorite": "j",
        "unfavorite": "j",
        "next": "down",
        "prev": "up",
        "forward": "right",
        "backward": "left",
        "fullscreen": "f",
        "mute": "m",
        "window": "w",
        "refresh": "f5",
        "danmu": "d",
    }

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": list(self.HOTKEYS.keys()),
                    "description": "抖音操作"
                },
            },
            "required": ["action"]
        }

    def execute(self, action: str) -> str:
        try:
            key = self.HOTKEYS.get(action)
            if not key:
                return f"未知操作: {action}"

            pyautogui.press(key)
            time.sleep(0.3)

            action_names = {
                "play": "播放",
                "pause": "暂停",
                "like": "点赞",
                "unlike": "取消点赞",
                "follow": "关注",
                "unfollow": "取消关注",
                "comment": "打开评论",
                "share": "分享",
                "favorite": "收藏",
                "unfavorite": "取消收藏",
                "next": "下一个",
                "prev": "上一个",
                "forward": "快进",
                "backward": "快退",
                "fullscreen": "全屏",
                "mute": "静音",
                "window": "小窗",
                "refresh": "刷新",
                "danmu": "弹幕",
            }
            return f"已执行: {action_names.get(action, action)}"
        except Exception as e:
            logger.error(f"DouyinTool 执行失败: {e}")
            return f"抖音控制失败: {e}"
