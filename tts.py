from models.base import TTSMetadata
from models.eleven import ElevenLabsTTS
from models.kokoro import KokoroTTS

MODELS = {
    "kokoro": KokoroTTS,
    "eleven": ElevenLabsTTS,
}


def text_to_mp3(text: str, output_mp3: str, model_name: str, speed: float = 1.0) -> TTSMetadata:
    return MODELS[model_name](text, output_mp3, speed=speed, pick_random_voice=True).text_to_mp3()
