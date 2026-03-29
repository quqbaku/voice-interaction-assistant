# Voice Interaction Assistant

基于 OpenClaw 架构理念的 Windows 语音助手，使用 LLM 作为核心大脑，通过 Tool Calling 机制调用各种 Windows 系统控制工具。

## 特性

- **多 LLM 支持**：MiniMax-M2.7 / OpenAI / Anthropic / Ollama
- **双交互模式**：文本模式 + 语音模式
- **Windows 系统控制**：音量、面板、锁屏、关机、重启、休眠
- **应用管理**：扫描、打开、关闭应用
- **抖音自动化**：键盘快捷键自动化
- **语音播报**：TTS + Windows 通知

## 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入 API Key：

```env
MINIMAX_API_KEY=your-minimax-key
```

### 3. 运行

```powershell
# 文本模式
python main.py --mode text

# 语音模式
python main.py --mode voice
```

## 项目架构

```
Voice Interaction Assistant
├── core/                    # 核心模块
│   ├── agent.py            # LLM Agent (MiniMax/OpenAI/Claude)
│   ├── config.py           # 配置加载
│   ├── memory.py           # 对话记忆
│   └── audio_io.py         # 音频输入输出
├── tools/                   # 工具层
│   ├── base.py             # Tool 基类
│   ├── windows_sys.py      # 系统控制
│   ├── app_manager.py      # 应用管理
│   ├── douyin_auto.py      # 抖音自动化
│   ├── perception.py       # 系统感知
│   └── feedback.py         # 用户反馈
├── config/                  # 配置
│   ├── config.yaml         # 主配置
│   └── app_map.json       # 应用映射
├── docs/                    # 文档
└── openclaw/               # OpenClaw 参考 (Phase 2)
```

## LLM 配置

编辑 `config/config.yaml` 中的 `llm` 部分：

```yaml
llm:
  default: "minimax"  # 可选: minimax / openai / anthropic / ollama
  providers:
    minimax:
      api_key: "${MINIMAX_API_KEY}"
      model: "MiniMax-M2.7"
      base_url: "https://api.minimaxi.com/v1"
```

## 扩展工具

创建 `tools/` 下的新 Tool 类：

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {"param": {"type": "string"}},
            "required": ["param"]
        }

    def execute(self, **kwargs) -> str:
        return f"结果: {kwargs.get('param')}"
```

## OpenClaw 集成 (Phase 2)

规划中：通过 OpenClaw CLI Backend 调用 Python 工具，复用 OpenClaw 多渠道和插件生态。

详见 [docs/openclaw-integration.md](docs/openclaw-integration.md)

## 文档

- [docs/README.md](docs/README.md) - 文档总览
- [docs/architecture.md](docs/architecture.md) - 系统架构
- [docs/tools.md](docs/tools.md) - 工具接口

## License

MIT
