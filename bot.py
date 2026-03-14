import telebot
import requests
from flask import Flask
import threading
import os

# 🔑 မင်းရဲ့ Bot Token
TOKEN = '8680632843:AAFIrkABpdfWTH9TwbrJeugUxM1eCWuhDiI'
bot = telebot.TeleBot(TOKEN)

# 🌐 API Link
API_URL = 'https://magic-mall-mlbb-id-check-v1.hlaaunghtun68.workers.dev/mobile-legends'

# Flask Web Server (၂၄ နာရီ မအိပ်အောင် လုပ်ပေးမည့်အပိုင်း)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 **MLBB Checker မှ ကြိုဆိုပါတယ်!**\n\nစစ်ရန်: `/check [ID] [Server]`", parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def handle_check(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "⚠️ ပုံစံ: `/check 1609968597 16765`", parse_mode="Markdown")
            return
        
        status_msg = bot.reply_to(message, "🔍 စစ်ဆေးနေပါသည်...")
        full_url = f"{API_URL}/{args[1]}/{args[2]}"
        data = requests.get(full_url, timeout=12).json()

        if data.get('error') or not data.get('data'):
            bot.edit_message_text("❌ အကောင့်မတွေ့ပါ!", chat_id=message.chat.id, message_id=status_msg.message_id)
            return

        info = data['data']
        res = f"🎯 **MLBB Info**\n👤 IGN: `{info.get('username')}`\n🌍 Region: {info.get('region')}\n"
        
        if info.get('shop_events'):
            res += "\n💎 **2x Status:**\n"
            for event in info['shop_events']:
                for item in event.get('goods', []):
                    status = "🔴 မရတော့ပါ" if item.get('reached_limit') else "🟢 ရနိုင်ပါသေးသည်"
                    res += f"• {item.get('title')} — {status}\n"

        bot.edit_message_text(res, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "🚫 Error!")

if __name__ == '__main__':
    # Flask ကို Background မှာ ပတ်မည်
    threading.Thread(target=run_flask).start()
    print("🚀 Bot is running...")
    bot.infinity_polling()
