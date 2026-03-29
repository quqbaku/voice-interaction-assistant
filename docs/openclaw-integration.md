# OpenClaw 集成计划

> Phase 2 - 规划中

## 背景

OpenClaw 是 TypeScript/Node.js 的 AI Agent 框架，本项目当前使用纯 Python 实现。集成 OpenClaw 可复用其多渠道插件生态。

## 关键发现

- OpenClaw 纯 TypeScript/Node.js，无官方 Python SDK
- CLI Backend 支持 stdin/stdout 通信
- 工具通过 `api.registerTool()` 注册

## 集成架构

```
OpenClaw (Node.js)
    │
    ├── CLI Backend
    │   command: python
    │   args: ["-m", "tools.cli_adapter"]
    │   input: stdin
    │   output: json
    │
    ▼
Python CLI Adapter
    │
    ├── windows_set_volume
    ├── windows_open_panel
    ├── app_launch / app_close
    ├── douyin_action
    └── audio_listen / audio_speak
```

## 实施步骤

### Step 1: Python CLI Adapter

创建 `tools/cli_adapter.py`：

```python
import sys, json

def main():
    cmd = json.loads(sys.stdin.read())
    tool_name = cmd.get("tool")
    args = cmd.get("args", {})

    result = execute_tool(tool_name, args)
    print(json.dumps(result))
```

### Step 2: OpenClaw 配置

创建 `openclaw/.agent/agents/<agent-id>/agents.yaml`：

```yaml
agents:
  defaults:
    cliBackends:
      - id: windows-tools
        command: python
        args: ["-m", "tools.cli_adapter"]
        input: stdin
        output: json
```

### Step 3: 验证

```bash
# CLI 测试
echo '{"tool":"windows_set_volume","args":{"level":50}}' | python -m tools.cli_adapter
```

## 工具清单

| 工具名 | 说明 | 参数 |
|--------|------|------|
| `windows_set_volume` | 设置音量 | `level: int` |
| `windows_open_panel` | 打开面板 | `panel: str` |
| `windows_lock` | 锁屏 | - |
| `windows_shutdown` | 关机 | - |
| `windows_screenshot` | 截图 | - |
| `app_launch` | 打开应用 | `name: str` |
| `app_close` | 关闭应用 | `name: str` |
| `douyin_action` | 抖音操作 | `action: str` |
| `audio_listen` | 语音识别 | `timeout: int` |
| `audio_speak` | 语音播报 | `text: str` |

## 替代方案

如无需 OpenClaw 多渠道支持，当前 Python Agent 已可独立工作。

## 参考资料

- OpenClaw 源码: `openclaw/`
- OpenClaw Docs: https://docs.openclaw.ai/
