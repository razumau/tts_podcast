from models.base import TTSMetadata
from models.eleven import ElevenLabsTTS
from models.kokoro import KokoroTTS

MODELS = {
    "kokoro": KokoroTTS,
    "eleven": ElevenLabsTTS,
}


def text_to_mp3(text: str, output_mp3: str, model_name: str, speed: float = 1.0) -> TTSMetadata:
    return MODELS[model_name](text, output_mp3, speed=speed, pick_random_voice=True).text_to_mp3()

if __name__ == "__main__":
    text = """For a developer, a Container image is essentially a collection of configurations required to run a container. But what really is a container image? You might know what a container image is, how it is made up of layers and that it’s a collection of tar archives. There are questions that still went unanswered, questions such as what makes up a layer, how are layers combined to form a complete filesystem or multi-platform images, etc. In this article, we’ll build a container image from scratch and try to answer all these questions to understand container image internals."""
    voices = ["af_sky", "af_aoede", "af_nova", "af_kore"]
    for voice in voices:
        print("Generating", voice)
        output_mp3 = f"{voice}.mp3"
        MODELS["kokoro"](text, output_mp3, speed=1.2, pick_random_voice=False, voice=voice).text_to_mp3()
