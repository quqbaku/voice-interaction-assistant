"""Windows Voice Assistant - 主入口"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from core import load_config, Agent, ConversationMemory, AppContext, create_audio_input, create_tts
from tools import SystemTool, AppTool, DouyinTool, PerceptionTool, FeedbackTool

# 加载 .env
load_dotenv()

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("assistant.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    """语音助手主类"""

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        self.memory = ConversationMemory()
        self.app_context = AppContext()
        self.agent = Agent(self.config)
        self.audio_input = create_audio_input(self.config)
        self.tts = create_tts(self.config)
        self._register_tools()

    def _register_tools(self):
        """注册所有工具"""
        tools = [
            SystemTool(),
            AppTool(self.config),
            DouyinTool(),
            PerceptionTool(),
            FeedbackTool(self.config.get("speech", {}).get("tts_engine", "pyttsx3")),
        ]
        self.agent.register_tools(tools)
        logger.info(f"已注册 {len(tools)} 个工具")

    def _check_wake_word(self, text: str) -> bool:
        """检查唤醒词"""
        wake_words = self.config.get("wake_words", [])
        return any(w in text for w in wake_words)

    def _extract_command(self, text: str) -> str:
        """提取命令（移除唤醒词）"""
        wake_words = self.config.get("wake_words", [])
        for w in wake_words:
            if w in text:
                return text.replace(w, "").strip()
        return text

    def run_text_mode(self):
        """文本交互模式"""
        print("=" * 50)
        print("Windows Voice Assistant - 文本模式")
        print("输入 'quit' 或 '退出' 退出程序")
        print("输入 'reset' 重置对话历史")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n你: ").strip()
                if not user_input:
                    continue

                if user_input in ["quit", "退出", "exit", "q"]:
                    print("助手: 再见！")
                    break

                if user_input in ["reset", "重置"]:
                    self.agent.reset()
                    self.memory.clear()
                    print("助手: 对话历史已重置")
                    continue

                # 注入上下文
                context = self.app_context.to_context_string()
                self.agent.add_context(f"[当前桌面状态]\n{context}")

                # 处理输入
                response = self.agent.think(user_input)
                self.memory.add("user", user_input)
                self.memory.add("assistant", response)

                print(f"\n助手: {response}")

            except KeyboardInterrupt:
                print("\n\n助手: 再见！")
                break
            except Exception as e:
                logger.error(f"处理输入失败: {e}")
                print(f"错误: {e}")

    def run_voice_mode(self):
        """语音交互模式"""
        print("=" * 50)
        print("Windows Voice Assistant - 语音模式")
        print("说 '退出' 退出程序")
        print("=" * 50)

        if not self.audio_input.is_available():
            print("警告: 语音识别不可用，切换到文本模式")
            self.run_text_mode()
            return

        self.tts.speak("语音助手已启动")

        while True:
            try:
                print("\n聆听中... (请说话)")
                audio_text = self.audio_input.listen(timeout=5)

                if not audio_text:
                    continue

                print(f"你: {audio_text}")

                # 检查退出
                if audio_text in ["退出", "quit", "exit", "关闭", "停止"]:
                    self.tts.speak("再见")
                    break

                # 检查唤醒词
                if not self._check_wake_word(audio_text):
                    print("未检测到唤醒词")
                    continue

                # 提取命令
                command = self._extract_command(audio_text)
                if not command:
                    continue

                print(f"命令: {command}")

                # 注入上下文
                context = self.app_context.to_context_string()
                self.agent.add_context(f"[当前桌面状态]\n{context}")

                # 处理
                response = self.agent.think(command)
                self.memory.add("user", command)
                self.memory.add("assistant", response)

                print(f"助手: {response}")
                self.tts.speak(response)

            except KeyboardInterrupt:
                print("\n\n助手: 再见！")
                break
            except Exception as e:
                logger.error(f"语音模式错误: {e}")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="Windows Voice Assistant")
    parser.add_argument("--mode", choices=["text", "voice"], default="text", help="交互模式")
    parser.add_argument("--config", type=str, help="配置文件路径")
    args = parser.parse_args()

    assistant = VoiceAssistant(args.config)

    if args.mode == "voice":
        assistant.run_voice_mode()
    else:
        assistant.run_text_mode()


if __name__ == "__main__":
    main()
