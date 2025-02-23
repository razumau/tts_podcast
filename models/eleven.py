import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

DEFAULT_VOICE = "Xb7hH8MSUJpSbSDYk0k2"


class ElevenLabsTTS:
    def __init__(self, text: str, output_filename: str, voice: str = DEFAULT_VOICE, _speed: float = 1.0):
        self.text = text
        self.output_filename = output_filename
        self.voice = voice
        self.model_id = "eleven_turbo_v2_5"
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def text_to_mp3(self):
        response = self.client.text_to_speech.convert(
            voice_id=self.voice,
            output_format="mp3_22050_32",
            text=self.text,
            model_id=self.model_id,
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        with open(self.output_filename, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
