import os
import telebot
import requests

# Fetches your Telegram Bot Token from Railway Environment Variables
# If running locally for testing, replace the os.getenv with your actual token string.
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(BOT_TOKEN)

# The public Cobalt API endpoint
COBALT_API_URL = "https://api.cobalt.tools/"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome! Send me a link from YouTube, Instagram, TikTok, or Twitter, "
        "and I will fetch the video for you."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    
    # Basic validation to ensure the user sent a link
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Please send a valid link (starting with http:// or https://).")
        return
        
    processing_msg = bot.reply_to(message, "⏳ Processing link via Cobalt... Please wait.")
    
    # Cobalt API requires these specific headers
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url
    }
    
    try:
        # Send the link to Cobalt
        response = requests.post(COBALT_API_URL, headers=headers, json=payload)
        data = response.json()
        
        # If Cobalt successfully parsed the video, it returns a direct 'url'
        if "url" in data:
            video_url = data["url"]
            bot.edit_message_text("⬇️ Sending video...", chat_id=message.chat.id, message_id=processing_msg.message_id)
            
            # Pass the direct URL to Telegram. Telegram servers will download and send it.
            bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, processing_msg.message_id)
        else:
            # If the API returns an error (e.g., private video, invalid link)
            error_status = data.get('status', 'Unknown error')
            bot.edit_message_text(f"❌ Cobalt failed to process this link. Status: {error_status}", 
                                  chat_id=message.chat.id, message_id=processing_msg.message_id)
            
    except Exception as e:
        # Catching network errors or Telegram API limits
        bot.edit_message_text(f"❌ An error occurred: {str(e)}\n\n(Note: Telegram bots have a 20MB file limit for URL uploads)", 
                              chat_id=message.chat.id, message_id=processing_msg.message_id)

if __name__ == "__main__":
    print("Bot is running and polling for messages...")
    bot.infinity_polling()
