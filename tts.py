from functools import partial

from chunking import split_text
from models.base import TTSMetadata
from models.eleven import ElevenLabsTTS
from models.kokoro import KokoroTTS

MODELS = {
    "kokoro": KokoroTTS,
    "eleven": ElevenLabsTTS,
    "eleven_v3": partial(ElevenLabsTTS, model_id="eleven_v3"),
    "eleven_v4": partial(ElevenLabsTTS, model_id="eleven_v4"),
}

# Longer texts are published as several episodes. ElevenLabs values are the API's per-request limits;
# Kokoro has no limit, so its value just keeps episodes around 20 minutes long.
MAX_CHARS_PER_EPISODE = {
    "kokoro": 20_000,
    "eleven": 40_000,
    "eleven_v3": 5_000,
    "eleven_v4": 10_000,
}


def split_for_model(text: str, model_name: str) -> list[str]:
    return split_text(text, MAX_CHARS_PER_EPISODE[model_name])


def text_to_mp3(
    text: str, output_mp3: str, model_name: str, speed: float = 1.0, voice: str | None = None
) -> TTSMetadata:
    """Picks a random voice unless one is given, e.g. to keep the voice of an earlier part."""
    if voice is None:
        return MODELS[model_name](text, output_mp3, speed=speed, pick_random_voice=True).text_to_mp3()
    return MODELS[model_name](text, output_mp3, speed=speed, voice=voice).text_to_mp3()
