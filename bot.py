import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # set this in Railway environment variables

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Video Downloader Bot!\n\n"
        "Just send me any YouTube or Instagram video link and I'll download it for you.\n\n"
        "Supported:\n"
        "✅ YouTube\n"
        "✅ Instagram Reels & Posts"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Basic URL check
    if "youtube.com" not in url and "youtu.be" not in url and "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube or Instagram link.")
        return

    await update.message.reply_text("⏳ Downloading your video, please wait...")

    output_path = f"downloads/{update.message.message_id}.mp4"
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Check file size (Telegram limit is 50MB)
        file_size = os.path.getsize(output_path)
        if file_size > 50 * 1024 * 1024:
            await update.message.reply_text("❌ Video is too large (over 50MB). Try a shorter video.")
            os.remove(output_path)
            return

        await update.message.reply_text("✅ Done! Sending your video...")
        with open(output_path, "rb") as video_file:
            await update.message.reply_video(video=video_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download. Make sure the link is public.\n\nError: {str(e)}")

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot is running...")
    app.run_polling()
