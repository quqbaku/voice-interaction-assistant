# 工具接口

## BaseTool 基类

所有工具继承自 `tools.base.BaseTool`：

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "工具描述"

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

## 工具清单

### SystemTool (`tools/windows_sys.py`)

Windows 系统控制工具。

**工具名**: `system_control`

**操作**:

| action | 说明 | 参数 |
|--------|------|------|
| `set_volume` | 设置音量 | `level: int (0-100)` |
| `get_volume` | 获取音量 | - |
| `mute` | 静音切换 | - |
| `lock` | 锁屏 | - |
| `shutdown` | 关机 | - |
| `restart` | 重启 | - |
| `sleep` | 睡眠 | - |
| `screenshot` | 截图 | - |
| `open_panel` | 打开面板 | `panel: str` |
| `empty_recycle_bin` | 清空回收站 | - |

**面板名称**: 设置, 控制面板, 任务管理器, 网络, 蓝牙, 声音, 显示, 个性化, 应用, 任务栏, 电源, 投影, 截图, 回收站

### AppTool (`tools/app_manager.py`)

应用管理工具。

**工具名**: `app_manager`

**操作**:

| action | 说明 | 参数 |
|--------|------|------|
| `scan` | 扫描应用 | - |
| `launch` | 打开应用 | `name: str` |
| `close` | 关闭应用 | `name: str` |
| `check` | 查询应用 | `name: str` |
| `list` | 列出应用 | - |

### DouyinTool (`tools/douyin_auto.py`)

抖音键盘自动化工具。

**工具名**: `douyin_control`

**操作**: play, pause, like, follow, comment, share, favorite, next, prev, forward, backward, fullscreen, mute, window, refresh, danmu

### PerceptionTool (`tools/perception.py`)

系统感知工具。

**工具名**: `system_perception`

**操作**:

| action | 说明 |
|--------|------|
| `focused_window` | 获取焦点窗口 |
| `running_processes` | 获取运行进程 |
| `screenshot` | 截图 |
| `volume` | 获取音量 |

### FeedbackTool (`tools/feedback.py`)

用户反馈工具。

**工具名**: `user_feedback`

**操作**:

| action | 说明 | 参数 |
|--------|------|------|
| `speak` | 语音播报 | `text: str` |
| `notify` | 发送通知 | `title: str, message: str` |
| `remind` | 定时提醒 | `message: str, seconds: int` |

## 注册工具

在 `main.py` 的 `_register_tools` 方法中注册：

```python
def _register_tools(self):
    tools = [
        SystemTool(),
        AppTool(self.config),
        DouyinTool(),
        PerceptionTool(),
        FeedbackTool(self.config.get("speech", {}).get("tts_engine", "pyttsx3")),
    ]
    self.agent.register_tools(tools)
```
