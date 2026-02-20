import os
import subprocess
import tempfile

from dia.model import Dia

from models.base import BaseTTS, TTSMetadata

# Dia generates its own speaker voices — no external voice selection.
# Speakers are controlled via [S1] and [S2] tags in the text.
DEFAULT_VOICE = "dia-default"

# Maximum recommended generation length per chunk (in characters).
# Dia v1 degrades beyond ~20 seconds of audio. At roughly 15 chars/second
# of speech, 250 chars per chunk is a safe target.
MAX_CHUNK_CHARS = 250


class DiaTTS(BaseTTS):
    def __init__(
        self,
        text: str,
        output_filename: str,
        pick_random_voice: bool = False,
        voice: str = DEFAULT_VOICE,
        speed: float = 1.0,
    ):
        self.text = text
        self.output_filename = output_filename
        self.voice = DEFAULT_VOICE
        self.speed = speed

    def text_to_mp3(self) -> TTSMetadata:
        model = Dia.from_pretrained("nari-labs/Dia-1.6B-0626", compute_dtype="float16")

        chunks = self._split_into_chunks(self.text)
        wav_files = []

        try:
            for i, chunk in enumerate(chunks):
                output = model.generate(
                    chunk,
                    use_torch_compile=False,
                    verbose=True,
                )
                wav_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
                model.save_audio(wav_path, output)
                wav_files.append(wav_path)

            self._concat_to_mp3(wav_files)
        finally:
            for f in wav_files:
                if os.path.exists(f):
                    os.remove(f)

        return TTSMetadata(model="dia", voice=self.voice)

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into chunks that respect speaker tag boundaries."""
        # Split on speaker tags while keeping the tags
        parts = []
        current = ""
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # If adding this line would exceed the limit, flush current
            if current and len(current) + len(line) + 1 > MAX_CHUNK_CHARS:
                parts.append(current.strip())
                current = ""
            current += " " + line
        if current.strip():
            parts.append(current.strip())

        # Ensure each chunk starts with a speaker tag
        result = []
        last_speaker = "[S1]"
        for part in parts:
            if not part.startswith("[S"):
                part = f"{last_speaker} {part}"
            # Track the last speaker tag used
            for tag in ["[S1]", "[S2]"]:
                if tag in part:
                    last_speaker = tag
            result.append(part)

        return result if result else [text]

    def _concat_to_mp3(self, wav_files: list[str]):
        """Concatenate WAV files into a single MP3 using ffmpeg."""
        if len(wav_files) == 1:
            cmd = [
                "ffmpeg", "-y", "-i", wav_files[0],
                "-c:a", "libmp3lame", "-b:a", "192k",
                self.output_filename,
            ]
            subprocess.run(cmd, check=True)
            return

        concat_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        try:
            for wav_file in wav_files:
                concat_file.write(f"file '{os.path.abspath(wav_file)}'\n")
            concat_file.close()

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_file.name,
                "-c:a", "libmp3lame", "-b:a", "192k",
                self.output_filename,
            ]
            subprocess.run(cmd, check=True)
        finally:
            os.remove(concat_file.name)
