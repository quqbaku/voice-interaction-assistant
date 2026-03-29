"""音频输入输出模块"""
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class AudioInput(ABC):
    """音频输入基类"""

    @abstractmethod
    def listen(self, timeout: int = 5) -> Optional[str]:
        """监听并返回识别文本"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass


class GoogleSTT(AudioInput):
    """Google 语音识别"""

    def __init__(self, language: str = "zh-CN"):
        self.language = language
        self._available = False
        self._check()

    def _check(self):
        try:
            import speech_recognition
            self.recognizer = speech_recognition.Recognizer()
            self._available = True
        except ImportError:
            logger.warning("SpeechRecognition 未安装")

    def listen(self, timeout: int = 5) -> Optional[str]:
        if not self._available:
            return None
        import speech_recognition as sr
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=timeout)
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except Exception as e:
            logger.warning(f"Google STT 识别失败: {e}")
            return None

    def is_available(self) -> bool:
        return self._available


class SherpaOnnxSTT(AudioInput):
    """Sherpa-onnx 本地语音识别"""

    def __init__(self, model_path: str, language: str = "zh-CN"):
        self.model_path = model_path
        self.language = language
        self._available = False
        self._init()

    def _init(self):
        try:
            import sherpa_onnx
            # 检查模型文件
            import os
            model_file = os.path.join(self.model_path, "model.int8.onnx")
            tokens_file = os.path.join(self.model_path, "tokens.txt")
            if os.path.exists(model_file) and os.path.exists(tokens_file):
                self._available = True
                logger.info("Sherpa-onnx 模型已加载")
            else:
                logger.warning(f"Sherpa-onnx 模型文件未找到: {model_file}")
        except ImportError:
            logger.warning("sherpa-onnx 未安装")

    def listen(self, timeout: int = 5) -> Optional[str]:
        if not self._available:
            return None
        # sherpa-onnx 录音识别逻辑
        # 简化实现，实际需要完整的录音->识别流程
        return None

    def is_available(self) -> bool:
        return self._available


class TTSOutput:
    """语音输出"""

    def __init__(self, engine: str = "pyttsx3"):
        self.engine = engine
        self._init()

    def _init(self):
        if self.engine == "pyttsx3":
            try:
                import pyttsx3
                self._tts = pyttsx3.init()
                logger.info("TTS (pyttsx3) 初始化完成")
            except Exception as e:
                logger.warning(f"TTS 初始化失败: {e}")
                self._tts = None
        elif self.engine == "edge-tts":
            # edge-tts 需要异步调用，简化处理
            self._tts = None

    def speak(self, text: str):
        """播报文本"""
        if self._tts:
            self._tts.say(text)
            self._tts.runAndWait()
        else:
            logger.info(f"[TTS] {text}")


def create_audio_input(config: dict) -> AudioInput:
    """工厂函数：创建音频输入"""
    speech_cfg = config.get("speech", {})
    engine = speech_cfg.get("engine", "google")

    if engine == "sherpaonnx":
        model_path = speech_cfg.get("model_path", "models/sense_voice")
        return SherpaOnnxSTT(model_path)
    return GoogleSTT(speech_cfg.get("language", "zh-CN"))


def create_tts(config: dict) -> TTSOutput:
    """工厂函数：创建 TTS"""
    speech_cfg = config.get("speech", {})
    return TTSOutput(speech_cfg.get("tts_engine", "pyttsx3"))
