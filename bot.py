import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Video Downloader Bot!\n\n"
        "Send me any YouTube or Instagram video link and I'll download it for you.\n\n"
        "Supported:\n"
        "✅ YouTube\n"
        "✅ Instagram Reels & Posts"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url and "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube or Instagram link.")
        return

    await update.message.reply_text("⏳ Downloading your video, please wait...")

    os.makedirs("downloads", exist_ok=True)
    output_path = f"downloads/{update.message.message_id}.mp4"

    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_size = os.path.getsize(output_path)
        if file_size > 50 * 1024 * 1024:
            await update.message.reply_text("❌ Video too large (over 50MB). Try a shorter video.")
            os.remove(output_path)
            return

        with open(output_path, "rb") as video_file:
            await update.message.reply_video(video=video_file, caption="✅ Here is your video!")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download.\nMake sure the link is public.\n\nError: {str(e)}")

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
