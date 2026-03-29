# 系统架构

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Interaction Assistant                │
├─────────────────────────────────────────────────────────────┤
│  Input Layer                                               │
│  ┌─────────────┐    ┌─────────────┐                       │
│  │ Text Mode  │    │ Voice Mode  │                       │
│  │  (stdin)   │    │ (sherpa-onnx)│                       │
│  └──────┬──────┘    └──────┬──────┘                       │
├─────────┴──────────────────┴───────────────────────────────┤
│  Core Layer                                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Agent (LLM)                         │   │
│  │  - MiniMax-M2.7 / OpenAI / Anthropic / Ollama        │   │
│  │  - Tool Calling                                       │   │
│  │  - 对话记忆 (ConversationMemory)                     │   │
│  └──────────────────────┬───────────────────────────────┘   │
├─────────────────────────┴─────────────────────────────────┤
│  Tools Layer                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ SystemTool  │ │ AppTool     │ │ DouyinTool          │ │
│  │ 音量/面板   │ │ 扫描/打开   │ │ 键盘自动化           │ │
│  ├─────────────┤ ├─────────────┤ ├─────────────────────┤ │
│  │ Perception  │ │ Feedback    │ │ (可扩展)            │ │
│  │ 感知能力    │ │ TTS/通知    │ │                     │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 模块说明

### core/agent.py

LLM Agent 核心模块，负责：
- LLM 客户端初始化（MiniMax/OpenAI/Claude/Ollama）
- 消息历史管理
- Tool Calling 处理
- 响应生成

### core/memory.py

对话记忆管理：
- `ConversationMemory`: 对话历史
- `AppContext`: 当前桌面状态（焦点窗口、音量、运行应用）

### core/audio_io.py

音频输入输出：
- `AudioInput`: 语音识别（Sherpa-onnx / Google STT）
- `TTSOutput`: 语音播报（pyttsx3）

### tools/*.py

工具实现：
- `SystemTool`: Windows 系统控制
- `AppTool`: 应用管理
- `DouyinTool`: 抖音键盘自动化
- `PerceptionTool`: 系统感知
- `FeedbackTool`: 用户反馈

## OpenClaw 集成架构 (Phase 2)

```
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw (Node.js) - Agent 大脑                           │
│  - LLM 对话管理 / 意图理解 / 工具调度                        │
│  - 多渠道支持 (Discord/Telegram 等)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ CLI Backend (stdin/stdout JSON)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Python Tools Layer                                        │
│  - windows_set_volume, windows_open_panel                  │
│  - app_launch, app_close                                   │
│  - douyin_action                                          │
│  - audio_listen, audio_speak                              │
└─────────────────────────────────────────────────────────────┘
```

详见 [OpenClaw 集成](openclaw-integration.md)
