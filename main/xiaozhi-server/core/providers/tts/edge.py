import os
import uuid
import edge_tts
from datetime import datetime
from core.providers.tts.base import TTSProviderBase


lang_proj_string = {
    "zn": "zh-CN-XiaoxiaoNeural",
    "en": "en-US-JennyNeural",
    "hk": "zh-HK-HiuGaaiNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "de": "de-AT-IngridNeural",
    "ar": "ar-BH-AliNeural",
    "es": "es-BO-SofiaNeural",
    "fr": "fr-BE-CharlineNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "pt": "pt-PT-RaquelNeural",
    "it": "it-IT-ElsaNeural",
    "th": "th-TH-PremwadeeNeural",
}


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.voice = config.get("voice")

    def generate_filename(self, extension=".mp3"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, text, output_file):
        communicate = edge_tts.Communicate(text, voice=self.voice)
        # 确保目录存在并创建空文件
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'wb') as f:
            pass
        
        # 流式写入音频数据
        with open(output_file, 'ab') as f:  # 改为追加模式避免覆盖
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":  # 只处理音频数据块
                    f.write(chunk["data"])

    def set_voice(self, voice_des):
        self.voice = lang_proj_string[voice_des]
