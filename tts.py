import string
import subprocess
import os
import random
import time

from kokoro import KPipeline
import soundfile as sf

DEFAULT_VOICE = "bf_emma"

def output_tts_to_wav_files(text: str, voice: str = DEFAULT_VOICE, speed: float = 1.0) -> list[str]:
    random_prefix = ''.join(random.choices(string.ascii_lowercase, k=15))
    pipeline = KPipeline(lang_code=voice[0])
    generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
    files_list = []
    for i, (graphemes, phonemes, audio) in enumerate(generator):
        filename = f'{random_prefix}_{i}.wav'
        sf.write(filename, audio, 24000)
        files_list.append(filename)

    print(f'Created {len(files_list)} files')
    return files_list


def concat_wav_to_mp3(wav_files: list[str], output_mp3: str, bitrate='192k'):
    with open('concat.txt', 'w') as f:
        for wav_file in wav_files:
            f.write(f"file '{os.path.abspath(wav_file)}'\n")

    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat.txt',
        '-c:a', 'libmp3lame',
        '-b:a', bitrate,
        output_mp3
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully created {output_mp3}")
        for wav_file in wav_files:
            os.remove(wav_file)
    finally:
        os.remove('concat.txt')


def text_to_mp3(text: str, output_mp3: str, speed: float = 1.0):
    start_time = time.time()
    wav_files = output_tts_to_wav_files(text, speed=speed)
    wav_end_time = time.time()
    print(f"Text to WAV took {wav_end_time - start_time} seconds.")
    concat_wav_to_mp3(wav_files, output_mp3)
    print(f"WAV to MP3 took {time.time() - wav_end_time} seconds.")

if __name__ == "__main__":
    files = [f'jkcwhptlmbkoisi_{i}.wav' for i in range(231)]
    concat_wav_to_mp3(files, 'output.mp3')
