# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TTS Podcast converts URLs sent via a Telegram bot into podcast episodes. The pipeline: extract article content (Bun/Readability.js) → preprocess text (regex or Claude LLM) → generate audio (Kokoro local TTS or ElevenLabs API) → convert to MP3 (ffmpeg) → upload to Cloudflare R2 → update RSS feed.

## Commands

```bash
# Install dependencies
uv sync --all-extras --dev
bun install

# Run the bot
python bot.py

# Tests
uv run python -m unittest discover tests
uv run python -m unittest tests.test_preprocess      # single test module
uv run python -m unittest tests.test_tts
uv run python -m unittest tests.test_extract_article

# Linting & formatting
uv run ruff check .
uv run ruff format --diff .    # check only
uv run ruff format .           # fix
```

Ruff line-length is 120 (configured in `pyproject.toml`).

## Architecture

**Hybrid stack:** Python backend + TypeScript/Bun for article extraction.

**Processing pipeline** (orchestrated by `bot.py`):

1. **`extract_article.py`** → spawns `bun extract_article.ts <url>` as a subprocess; uses Mozilla Readability to extract title and text content
2. **Preprocessing** (user-selectable per chat):
   - `"none"` — raw text
   - `"regex"` — `preprocess.py`: 13-step regex pipeline (removes markdown/HTML, expands abbreviations and numbers via `num2words`)
   - `"llm"` — `llm_preprocess.py`: rewrites text for natural audio narration using Claude Haiku
3. **`tts.py`** → delegates to a TTS model from `models/`:
   - `models/base.py` — `BaseTTS` abstract class and `TTSMetadata` dataclass
   - `models/kokoro.py` — local Kokoro-82M TTS (13 voices, 24kHz WAV, concatenated to MP3)
   - `models/eleven.py` — ElevenLabs API (Flash v2.5 and v3 model variants)
   - `MODELS` dict in `tts.py` maps model names to classes
4. **`podcast.py`** → `PodcastFeed` uploads MP3 to Cloudflare R2, generates/updates RSS feed with iTunes podcast extensions

**Telegram bot commands** (`bot.py`): `/start`, `/setmodel <model>`, `/setpreprocess <mode>`. Text messages with URLs trigger the pipeline. Access controlled by username/ID whitelist in env vars.

## System Requirements

Python 3.12+, Bun, ffmpeg, uv (package manager).
