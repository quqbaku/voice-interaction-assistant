"""LLM Agent 模块 - 基于 OpenClaw 架构，支持 MiniMax/OpenAI/Claude/Ollama"""
import os
import json
import logging
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class Agent:
    """LLM Agent"""

    SYSTEM_PROMPT = """你是 Windows 桌面效率助手，名叫"小助手"。
你的职责是帮助用户通过自然语言高效地完成电脑操作任务。

## 你的能力
1. **系统控制**：调节音量、开关设置面板、截图、锁屏、关机、重启、休眠
2. **应用管理**：打开和关闭应用程序、查询已安装应用
3. **抖音自动化**：点赞、评论、关注、暂停、播放、快进、快退等
4. **文件操作**：创建文件夹、保存文件、列出目录
5. **提醒功能**：设置定时提醒，通过 Windows 通知提醒用户

## 行为规范
- 始终使用中文回复
- 执行操作后告知用户结果
- 如果操作失败，解释原因并提供替代方案
- 涉及危险操作（关机、重启）时需二次确认
- 保持回复简洁明了，避免冗长解释
- 主动询问是否需要其他帮助

## 上下文理解
- 支持指代理解（"打开它"指代上一次提到的应用）
- 支持模糊指令（"打一微信"自动理解为"打开微信"）
- 支持多步骤任务（"打开抖音，调低音量，然后全屏"）
"""

    def __init__(self, config: dict):
        self.config = config
        self.messages = []
        self.tools = []
        self.provider = None
        self.model = None
        self.temperature = None
        self.max_tokens = None
        self.reasoning_split = False
        self.client = None
        self._init_llm()

    def _init_llm(self):
        """初始化 LLM 客户端"""
        llm_cfg = self.config.get("llm", {})
        default_provider = llm_cfg.get("default", "minimax")
        providers = llm_cfg.get("providers", {})

        self.provider = default_provider
        provider_cfg = providers.get(default_provider, {})

        api_key = provider_cfg.get("api_key", "")

        # MiniMax 使用 OpenAI 兼容接口
        if default_provider == "minimax":
            api_key = api_key or os.environ.get("MINIMAX_API_KEY")
            self.client = OpenAI(
                api_key=api_key,
                base_url=provider_cfg.get("base_url", "https://api.minimaxi.com/v1")
            )
            self.model = provider_cfg.get("model", "MiniMax-M2.7")
            self.reasoning_split = provider_cfg.get("reasoning_split", True)
            self.temperature = provider_cfg.get("temperature", 1.0)
            self.max_tokens = provider_cfg.get("max_tokens", 4096)

        elif default_provider == "openai":
            api_key = api_key or os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key, base_url=provider_cfg.get("base_url"))
            self.model = provider_cfg.get("model", "gpt-4o")
            self.temperature = provider_cfg.get("temperature", 0.7)
            self.max_tokens = provider_cfg.get("max_tokens", 2000)

        elif default_provider == "anthropic":
            from anthropic import Anthropic
            api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            self.client = Anthropic(api_key=api_key)
            self.model = provider_cfg.get("model", "claude-sonnet-4-20250514")
            self.temperature = provider_cfg.get("temperature", 0.7)
            self.max_tokens = provider_cfg.get("max_tokens", 2000)

        elif default_provider == "ollama":
            self.client = OpenAI(
                base_url=provider_cfg.get("base_url", "http://localhost:11434/v1")
            )
            self.model = provider_cfg.get("model", "llama3")
            self.temperature = provider_cfg.get("temperature", 0.7)
            self.max_tokens = provider_cfg.get("max_tokens", 4096)
        else:
            raise ValueError(f"不支持的 LLM 提供商: {default_provider}")

        logger.info(f"LLM 初始化完成: {default_provider}/{self.model}")

    def register_tools(self, tools: list):
        """注册工具列表"""
        self.tools = tools

    def add_context(self, context: str):
        """添加上下文信息"""
        self.messages.append({"role": "system", "content": context})

    def think(self, user_input: str) -> str:
        """处理用户输入，返回助手回复"""
        self.messages.append({"role": "user", "content": user_input})

        # 构建工具描述
        tool_descs = []
        for tool in self.tools:
            tool_descs.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.get_schema()
                }
            })

        try:
            if self.provider == "anthropic":
                response = self._call_anthropic(tool_descs)
            else:
                response = self._call_openai_compatible(tool_descs)

            return response

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return f"抱歉，发生了错误: {e}"

    def _call_openai_compatible(self, tool_descs: list) -> str:
        """调用 OpenAI 兼容接口（MiniMax/OpenAI/Ollama）"""
        extra_body = {}

        # MiniMax 特殊参数
        if self.provider == "minimax" and self.reasoning_split:
            extra_body["reasoning_split"] = True

        # MiniMax 不支持 system role，将 system prompt 合并到第一条 user 消息
        if self.provider == "minimax":
            messages = []
            system_content = self.SYSTEM_PROMPT
            # 处理已有的消息
            for msg in self.messages:
                if msg["role"] == "system":
                    # 合并 system 到 user 消息
                    system_content += "\n\n" + msg["content"]
                else:
                    if msg["role"] == "user" and system_content:
                        # 将 system 内容合并到 user 消息
                        msg["content"] = f"[系统上下文]\n{system_content}\n\n[用户指令]\n{msg['content']}"
                        system_content = ""
                    messages.append(msg)
            if system_content:
                # 没有 user 消息，创建一个
                messages.insert(0, {"role": "user", "content": f"{system_content}\n\n用户: 你好"})
        else:
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}] + self.messages

        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if tool_descs:
            params["tools"] = tool_descs

        if extra_body:
            params["extra_body"] = extra_body

        response = self.client.chat.completions.create(**params)
        assistant_msg = response.choices[0].message

        # MiniMax 的 reasoning_details 处理
        reasoning_text = ""
        if hasattr(assistant_msg, "reasoning_details") and assistant_msg.reasoning_details:
            reasoning_text = assistant_msg.reasoning_details[0].get("text", "") or ""
            try:
                logger.debug(f"思维链: {reasoning_text[:100]}")
            except Exception:
                logger.debug("思维链: [内容包含特殊字符]")

        # 构建 assistant 消息（保留完整结构）
        assistant_content = assistant_msg.content or ""
        msg_dict = {
            "role": "assistant",
            "content": assistant_content,
        }
        if assistant_msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_msg.tool_calls
            ]

        self.messages.append(msg_dict)

        # 处理工具调用
        if assistant_msg.tool_calls:
            return self._handle_tool_calls(assistant_msg.tool_calls)

        return assistant_content or "好的，我明白了。"

    def _call_anthropic(self, tool_descs: list) -> str:
        """调用 Anthropic 接口"""
        # Anthropic 不支持 system 消息，需要合并到第一条 user 消息
        system_msg = {"role": "system", "content": self.SYSTEM_PROMPT}
        all_messages = [system_msg] + self.messages

        params = {
            "model": self.model,
            "messages": all_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if tool_descs:
            params["tools"] = tool_descs

        response = self.client.messages.create(**params)

        # 处理响应
        thinking_blocks = []
        text_blocks = []
        tool_use_blocks = []

        for block in response.content:
            if block.type == "thinking":
                thinking_blocks.append(block.thinking)
            elif block.type == "text":
                text_blocks.append(block.text)
            elif block.type == "tool_use":
                tool_use_blocks.append(block)

        # 记录思维链
        if thinking_blocks:
            logger.debug(f"思维链: {thinking_blocks[0][:100]}...")

        # 构建 assistant 消息（Anthropic 格式）
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })

        if tool_use_blocks:
            return self._handle_anthropic_tool_calls(tool_use_blocks)

        return text_blocks[0] if text_blocks else "好的，我明白了。"

    def _handle_tool_calls(self, tool_calls) -> str:
        """处理 OpenAI 兼容接口的工具调用"""
        results = []
        for call in tool_calls:
            tool_name = call.function.name
            args = json.loads(call.function.arguments)

            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        result = tool.execute(**args)
                        results.append(f"[{tool_name}] {result}")
                    except Exception as e:
                        results.append(f"[{tool_name}] 执行失败: {e}")
                    break

        # 添加工具结果到消息历史
        for call in tool_calls:
            self.messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": next(
                    (r for r in results if f"[{call.function.name}]" in r),
                    ""
                ).split("]", 1)[-1].strip()
            })

        # 再次调用获取最终回复
        return self._call_openai_compatible([])

    def _handle_anthropic_tool_calls(self, tool_use_blocks) -> str:
        """处理 Anthropic 接口的工具调用"""
        results = []
        for block in tool_use_blocks:
            tool_name = block.name
            args = block.input

            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        result = tool.execute(**args)
                        results.append(f"[{tool_name}] {result}")
                    except Exception as e:
                        results.append(f"[{tool_name}] 执行失败: {e}")
                    break

        # 添加工具结果
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": next(
                        (r for r in results if f"[{block.name}]" in r),
                        ""
                    ).split("]", 1)[-1].strip()
                }
                for block in tool_use_blocks
            ]
        })

        # 再次调用获取最终回复
        return self._call_anthropic([])

    def reset(self):
        """重置对话历史"""
        self.messages = []
