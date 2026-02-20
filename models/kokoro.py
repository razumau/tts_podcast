import string
import subprocess
import os
import random
import tempfile

from kokoro import KPipeline
import soundfile as sf

from models.base import BaseTTS, TTSMetadata

GOOD_VOICES = [
    "af_heart",
    "af_bella",
    "af_nova",
    "af_sarah",
    "af_jessica",
    "am_adam",
    "am_michael",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_george",
]


class KokoroTTS(BaseTTS):
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
        self.speed = speed
        self.wav_files = []

    def text_to_mp3(self) -> TTSMetadata:
        self.output_tts_to_wav_files()
        self.concat_wav_to_mp3()
        return TTSMetadata(model="kokoro", voice=self.voice)

    def output_tts_to_wav_files(self):
        random_prefix = "".join(random.choices(string.ascii_lowercase, k=15))
        pipeline = KPipeline(lang_code=self.voice[0], repo_id="hexgrad/Kokoro-82M")
        generator = pipeline(self.text, voice=self.voice, speed=self.speed, split_pattern=r"\n+")
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            filename = f"{random_prefix}_{i}.wav"
            sf.write(filename, audio, 24000)
            self.wav_files.append(filename)

        print(f"Created {len(self.wav_files)} files")

    def concat_wav_to_mp3(self):
        concat_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        try:
            for wav_file in self.wav_files:
                concat_file.write(f"file '{os.path.abspath(wav_file)}'\n")
            concat_file.close()

            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file.name,
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                self.output_filename,
            ]

            subprocess.run(cmd, check=True)
            print(f"Successfully created {self.output_filename}")
        finally:
            os.remove(concat_file.name)
            for wav_file in self.wav_files:
                if os.path.exists(wav_file):
                    os.remove(wav_file)
