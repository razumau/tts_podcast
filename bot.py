import os
import time

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import re

from dotenv import load_dotenv

from extract_article import extract_webpage_content
from preprocess import preprocess_for_tts
from llm_preprocess import rewrite_for_audio
from podcast import add_episode
from tts import text_to_mp3, MODELS

load_dotenv()

PREPROCESS_MODES = {
    "none": "No preprocessing (raw text)",
    "regex": "Regex-based cleaning (remove URLs, code, citations, expand numbers)",
    "llm": "LLM rewrite for natural audio narration",
}
DEFAULT_PREPROCESS = "llm"


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")


def allowed_user_ids() -> list[int]:
    try:
        return list(map(int, os.getenv("ALLOWED_TELEGRAM_IDS", "").split(",")))
    except ValueError:
        return []


def allowed_usernames() -> list[str]:
    return os.getenv("ALLOWED_TELEGRAM_USERNAMES", "").split(",")


def is_allowed(user_info) -> bool:
    if os.getenv("ALLOW_ALL_TELEGRAM_USERS") in ("true", "1", "yes"):
        return True
    return user_info.id in allowed_user_ids() or user_info.username in allowed_usernames()


async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not is_allowed(user):
        print(f"User {user} is not allowed")
        return

    if len(context.args) != 1 or context.args[0] not in MODELS.keys():
        await update.message.reply_text(f"Usage: /setmodel <model>\nAvailable models: {', '.join(MODELS.keys())}")
        return

    model = context.args[0]
    context.user_data["model"] = model
    await update.message.reply_text(f"Model set to {model}")


async def set_preprocess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not is_allowed(user):
        print(f"User {user} is not allowed")
        return

    if len(context.args) != 1 or context.args[0] not in PREPROCESS_MODES:
        modes_list = "\n".join(f"  {k}: {v}" for k, v in PREPROCESS_MODES.items())
        await update.message.reply_text(f"Usage: /setpreprocess <mode>\nAvailable modes:\n{modes_list}")
        return

    mode = context.args[0]
    context.user_data["preprocess"] = mode
    await update.message.reply_text(f"Preprocessing set to: {mode} — {PREPROCESS_MODES[mode]}")


async def apply_preprocessing(content: str, mode: str) -> str:
    if mode == "none":
        return content
    elif mode == "regex":
        return preprocess_for_tts(content)
    elif mode == "llm":
        return await rewrite_for_audio(preprocess_for_tts(content))
    return content


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not is_allowed(user):
        print(f"User {user} is not allowed")
        return

    default_model_name = next(iter(MODELS.keys()))
    model_name = context.user_data.get("model", default_model_name)
    preprocess_mode = context.user_data.get("preprocess", DEFAULT_PREPROCESS)

    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, update.message.text)

    if not urls:
        await update.message.reply_text("No URLs in the message, nothing to add")
        return

    if len(urls) > 1:
        await update.message.reply_text(f"Found {len(urls)} URLs, processing them one by one")

    for url in urls:
        start_time = time.time()
        result = extract_webpage_content(url)
        if result is None:
            await update.message.reply_text(f"Failed to extract content from {url}")
            continue

        title, content = result
        base_name = title.replace(" ", "_").lower()
        mp3_filename = base_name + ".mp3"

        os.makedirs("texts", exist_ok=True)
        with open(os.path.join("texts", base_name + ".raw.txt"), "w") as f:
            f.write(content)

        preprocessed_path = os.path.join("texts", base_name + f".{preprocess_mode}.txt")
        if os.path.exists(preprocessed_path):
            with open(preprocessed_path) as f:
                content = f.read()
            await update.message.reply_text(f"Using cached {preprocess_mode}-preprocessed text")
        else:
            await update.message.reply_text(f"Extracted content, preprocessing ({preprocess_mode})...")
            content = await apply_preprocessing(content, preprocess_mode)
            with open(preprocessed_path, "w") as f:
                f.write(content)

        await update.message.reply_text("Producing audio...")
        metadata = text_to_mp3(text=content, output_mp3=mp3_filename, model_name=model_name, speed=1.0)
        await update.message.reply_text("Produced audio, updating feed")
        description = (
            f"Model: {metadata.model}. Voice: {metadata.voice}. Preprocess: {preprocess_mode}. {content[:150]}"
        )
        add_episode(mp3_filename, title, description=description)
        end_time = time.time()
        await update.message.reply_text(
            f"Added \u201c{title}\u201d to the feed. This took {end_time - start_time:.2f} seconds"
        )

    if len(urls) > 1:
        await update.message.reply_text(f"Processed {len(urls)} URLs")


def main():
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setmodel", set_model))
    application.add_handler(CommandHandler("setpreprocess", set_preprocess))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
