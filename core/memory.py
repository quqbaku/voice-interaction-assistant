"""对话记忆模块"""
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """记忆条目"""
    role: str  # user / assistant / system
    content: str
    tool_calls: Optional[list] = None


class ConversationMemory:
    """对话记忆管理器"""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: list[MemoryEntry] = []

    def add(self, role: str, content: str, tool_calls: list = None):
        """添加记忆"""
        self.history.append(MemoryEntry(role=role, content=content, tool_calls=tool_calls))
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self, max_turns: int = 10) -> str:
        """获取最近 N 轮对话上下文"""
        recent = self.history[-max_turns * 2:] if self.history else []
        lines = []
        for entry in recent:
            role_label = "用户" if entry.role == "user" else "助手"
            lines.append(f"{role_label}: {entry.content}")
        return "\n".join(lines)

    def get_last_intent(self) -> Optional[str]:
        """获取上一轮助手意图"""
        for entry in reversed(self.history):
            if entry.role == "assistant" and entry.tool_calls:
                return entry.tool_calls[0].get("name") if isinstance(entry.tool_calls[0], dict) else None
        return None

    def clear(self):
        """清空记忆"""
        self.history.clear()


class AppContext:
    """应用上下文（当前桌面状态）"""

    def __init__(self):
        self.focused_window: str = ""
        self.volume: int = 50
        self.running_apps: list[str] = []

    def to_context_string(self) -> str:
        """转换为上下文字符串"""
        parts = []
        if self.focused_window:
            parts.append(f"当前窗口: {self.focused_window}")
        parts.append(f"当前音量: {self.volume}%")
        if self.running_apps:
            parts.append(f"运行中的应用: {', '.join(self.running_apps[:5])}")
        return "\n".join(parts) if parts else "无特殊上下文"
