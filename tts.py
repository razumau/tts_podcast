from models.kokoro import KokoroTTS

def text_to_mp3(text: str, output_mp3: str, speed: float = 1.0):
    KokoroTTS(text, output_mp3, speed=speed).text_to_mp3()
