# Voice Interaction Assistant

基于 OpenClaw 架构理念的 Windows 语音助手，使用 LLM 作为核心大脑，通过 Tool Calling 机制调用各种 Windows 系统控制工具。

## 项目简介

本项目是一个运行在 Windows 平台上的智能语音助手，核心采用 LLM 大语言模型，支持文本和语音两种交互方式。通过模块化的工具系统，可以执行音量控制、应用管理、抖音自动化等 Windows 系统操作。

## 主要特性

- **多 LLM 支持**：MiniMax-M2.7 / OpenAI / Anthropic / Ollama，可灵活切换
- **双交互模式**：文本模式（终端输入）+ 语音模式（语音识别）
- **Windows 系统控制**：音量调节、面板打开、锁屏、关机、重启、休眠、截图
- **应用管理**：扫描已安装应用、打开/关闭指定应用
- **抖音自动化**：键盘快捷键自动化操作（播放/暂停/点赞/评论等）
- **语音播报**：TTS 语音合成 + Windows 系统通知
- **对话记忆**：支持多轮对话上下文管理

## 系统要求

- Windows 10/11 系统
- Python 3.8+
- MiniMax API Key（或其他 LLM 提供者的 API Key）

## 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
MINIMAX_API_KEY=your-minimax-api-key
```

### 3. 运行程序

```powershell
# 文本模式（通过终端交互）
python main.py --mode text

# 语音模式（通过语音交互）
python main.py --mode voice
```

## 项目结构

```
Voice Interaction Assistant
├── main.py                 # 程序入口
├── core/                   # 核心模块
│   ├── agent.py           # LLM Agent（多 Provider 支持）
│   ├── config.py          # 配置加载模块
│   ├── memory.py          # 对话记忆管理
│   └── audio_io.py        # 音频输入输出（TTS/STT）
├── tools/                  # 工具层
│   ├── base.py            # Tool 基类
│   ├── windows_sys.py     # Windows 系统控制
│   ├── app_manager.py     # 应用管理
│   ├── douyin_auto.py     # 抖音键盘自动化
│   ├── perception.py       # 系统感知
│   └── feedback.py         # 用户反馈（TTS/通知）
├── config/                  # 配置目录
│   ├── config.yaml        # 主配置文件
│   └── app_map.json       # 应用名称映射
├── models/                  # 模型文件（语音识别等）
├── plugins/                 # 插件目录
└── docs/                    # 详细文档
```

## 配置说明

### LLM 配置

编辑 `config/config.yaml` 中的 `llm` 部分：

```yaml
llm:
  default: "minimax"  # 默认 provider
  providers:
    minimax:
      api_key: "${MINIMAX_API_KEY}"
      model: "MiniMax-M2.7"
      base_url: "https://api.minimaxi.com/v1"
      temperature: 1.0
      max_tokens: 4096
    openai:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4"
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      model: "claude-3-5-sonnet"
    ollama:
      model: "llama3"
      base_url: "http://localhost:11434"
```

### 工具配置

可在 `config/config.yaml` 中配置各工具参数。

## 内置工具

| 工具名称 | 功能描述 |
|---------|---------|
| `system_control` | Windows 系统控制（音量、面板、锁屏、关机等） |
| `app_manager` | 应用管理（扫描、打开、关闭、查询应用） |
| `douyin_control` | 抖音键盘自动化操作 |
| `system_perception` | 系统感知（焦点窗口、进程列表、截图） |
| `user_feedback` | 用户反馈（语音播报、通知、定时提醒） |

详细工具接口请参阅 [docs/tools.md](docs/tools.md)。

## 扩展开发

### 创建自定义工具

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"

    def get_schema(self) -> dict:
        """返回 JSON Schema 格式的参数定义"""
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "参数说明"}
            },
            "required": ["param"]
        }

    def execute(self, **kwargs) -> str:
        """执行工具逻辑，返回结果字符串"""
        return f"执行结果: {kwargs.get('param')}"
```

### 注册工具

在 `main.py` 的 `_register_tools` 方法中将工具添加到列表：

```python
def _register_tools(self):
    tools = [
        SystemTool(),
        AppTool(self.config),
        DouyinTool(),
        PerceptionTool(),
        FeedbackTool(self.config.get("speech", {}).get("tts_engine", "pyttsx3")),
        MyTool(),  # 添加自定义工具
    ]
    self.agent.register_tools(tools)
```

## OpenClaw 集成规划（Phase 2）

OpenClaw 是 TypeScript/Node.js 的 AI Agent 框架。本项目规划通过 OpenClaw CLI Backend 机制调用 Python 工具层，以复用 OpenClaw 的多渠道插件生态（如 Discord、Telegram 等）。

架构详情请参阅 [docs/openclaw-integration.md](docs/openclaw-integration.md)。

## 详细文档

- [docs/README.md](docs/README.md) - 文档目录
- [docs/architecture.md](docs/architecture.md) - 系统架构设计
- [docs/tools.md](docs/tools.md) - 工具接口文档
- [docs/openclaw-integration.md](docs/openclaw-integration.md) - OpenClaw 集成计划

## 技术栈

- **语言**：Python 3.8+
- **LLM**：MiniMax-M2.7 / OpenAI / Anthropic / Ollama
- **语音识别**：Sherpa-onnx（本地）
- **语音合成**：pyttsx3
- **系统控制**：pycaw、psutil、pyautogui、ScreenCapture

## License

MIT
