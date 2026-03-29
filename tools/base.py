"""Tool 基类"""
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Tool 基类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def get_schema(self) -> dict:
        """返回 JSON Schema 格式的参数定义"""
        return {"type": "object", "properties": {}}

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行工具逻辑"""
        pass
