import os
import telebot
import requests
import urllib3

# This forces Python to ignore that certificate error and silences the warning messages
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(BOT_TOKEN)

COBALT_API_URL = "https://melon.clxxped.lol/"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me a link from YouTube, Instagram, TikTok, or Twitter, and I will fetch the video for you.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Please send a valid link.")
        return
        
    processing_msg = bot.reply_to(message, "⏳ Processing link via Cobalt... Please wait.")
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url
    }
    
    try:
        # verify=False is the magic bullet here that skips the SSL check entirely
        response = requests.post(COBALT_API_URL, headers=headers, json=payload, verify=False)
        data = response.json()
        
        if "url" in data:
            video_url = data["url"]
            bot.edit_message_text("⬇️ Sending video...", chat_id=message.chat.id, message_id=processing_msg.message_id)
            bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, processing_msg.message_id)
        else:
            error_status = data.get('status', 'Unknown error')
            bot.edit_message_text(f"❌ Cobalt failed to process this link. Status: {error_status}", 
                                  chat_id=message.chat.id, message_id=processing_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ An error occurred: {str(e)}", 
                              chat_id=message.chat.id, message_id=processing_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
