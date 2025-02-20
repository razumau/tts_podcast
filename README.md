# TTS podcast

Creates a podcast feed from URLs sent to a Telegram bot.

1. Receives a message with a URL.
2. Runs a wrapper around [Readability.js](https://github.com/mozilla/readability) using Bun, extracts article and its title.
3. Creates a bunch of wav files using [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) as a TTS model.
4. Converts these wav files into a single mp3 with ffmpeg.
5. Uploads this mp3 to Cloudflare R2, updates feed.xml.
6. You can now listen to this URL using a podcast app on your phone!

Needs [Bun](https://bun.sh/) and ffmpeg installed. Uses uv for Python dependencies.

## To do

* Switch between different Kokoro voices
* Allow using other TTS models
* A browser extension
