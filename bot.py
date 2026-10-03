import os
import threading
from flask import Flask, send_from_directory, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "سلام 👋\nویدئو را همینجا برای من بفرست."
    )


@bot.message_handler(content_types=["video"])
def receive_video(message):
    try:
        bot.reply_to(
            message,
            "ویدئو دریافت شد ✅\nدر حال دریافت فایل..."
        )

        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = f"{message.video.file_unique_id}.mp4"

        with open(os.path.join(VIDEO_FOLDER, file_name), "wb") as f:
            f.write(downloaded_file)

        video_url = request.host_url.rstrip("/") + "/videos/" + file_name

        bot.reply_to(
            message,
            f"ویدئو با موفقیت دریافت شد ✅\n\n"
            f"لینک ویدئو:\n{video_url}"
        )

    except Exception as e:
        bot.reply_to(
            message,
            f"خطا در دریافت ویدئو: {e}"
        )


@app.route("/", methods=["GET"])
def home():
    return "Telegram Video Bot is running."


@app.route("/videos/<path:filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)


def run_bot():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
