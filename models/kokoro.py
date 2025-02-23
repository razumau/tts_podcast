import string
import subprocess
import os
import random

from kokoro import KPipeline
import soundfile as sf

DEFAULT_VOICE = "bf_emma"

class KokoroTTS:
    def __init__(self, text: str, output_filename: str, voice: str = DEFAULT_VOICE, speed: float = 1.0, bitrate: str ="192k"):
        self.text = text
        self.output_filename = output_filename
        self.voice = voice
        self.speed = speed
        self.bitrate = bitrate
        self.wav_files = []

    def text_to_mp3(self):
        self.output_tts_to_wav_files()
        self.concat_wav_to_mp3()

    def output_tts_to_wav_files(self):
        random_prefix = "".join(random.choices(string.ascii_lowercase, k=15))
        pipeline = KPipeline(lang_code=self.voice[0])
        generator = pipeline(self.text, voice=self.voice, speed=self.speed, split_pattern=r"\n+")
        for i, (graphemes, phonemes, audio) in enumerate(generator):
            filename = f"{random_prefix}_{i}.wav"
            sf.write(filename, audio, 24000)
            self.wav_files.append(filename)

        print(f"Created {len(self.wav_files)} files")

    def concat_wav_to_mp3(self):
        with open("concat.txt", "w") as f:
            for wav_file in self.wav_files:
                f.write(f"file '{os.path.abspath(wav_file)}'\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "concat.txt",
            "-c:a",
            "libmp3lame",
            "-b:a",
            self.bitrate,
            self.output_filename,
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully created {self.output_filename}")
            for wav_file in self.wav_files:
                os.remove(wav_file)
        finally:
            os.remove("concat.txt")
