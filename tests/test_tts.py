import os
import unittest
import glob
from tts import text_to_mp3

MP3_FILE = "test.mp3"


class TestTTS(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(MP3_FILE):
            os.remove(MP3_FILE)
        for wav_file in glob.glob("*.wav"):
            os.remove(wav_file)

    def test_tts(self):
        test_text = "This text will be read out loud."
        text_to_mp3(test_text, MP3_FILE, speed=1.0)
        self.assertTrue(os.path.exists(MP3_FILE), "MP3 file was not created")

        wav_files = glob.glob("*.wav")
        self.assertEqual(len(wav_files), 0, ".wav files remain in the folder")


if __name__ == "__main__":
    unittest.main()
