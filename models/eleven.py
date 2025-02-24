import os
import random

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from models.base import BaseTTS

GOOD_VOICES = ["Xb7hH8MSUJpSbSDYk0k2", "XB0fDUnXU5powFXDhCwa", "onwK4e9ZLuTAKqWW03F9", "ThT5KcBeYPX3keUQqHPh"]


class ElevenLabsTTS(BaseTTS):
    def __init__(
        self,
        text: str,
        output_filename: str,
        pick_random_voice: bool = False,
        voice: str = GOOD_VOICES[0],
        speed: float = 1.0,
    ):
        self.text = text
        self.output_filename = output_filename
        if pick_random_voice:
            self.voice = random.choice(GOOD_VOICES)
        else:
            self.voice = voice
        self.model_id = "eleven_flash_v2_5"
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
