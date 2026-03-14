import telebot
import requests
from flask import Flask
import threading
import os

TOKEN = '8680632843:AAFIrkABpdfWTH9TwbrJeugUxM1eCWuhDiI'
bot = telebot.TeleBot(TOKEN)
API_URL = 'https://magic-mall-mlbb-id-check-v1.hlaaunghtun68.workers.dev/mobile-legends'

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 **MLBB Checker (Fixed) မှ ကြိုဆိုပါတယ်!**\n\nစစ်ရန်: `/check [ID] [Server]`\nဥပမာ: `/check 1609968597 16765`", parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def handle_check(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "⚠️ ပုံစံ: `/check 1609968597 16765`", parse_mode="Markdown")
            return
        
        status_msg = bot.reply_to(message, "🔍 စစ်ဆေးနေပါသည်...")
        full_url = f"{API_URL}/{args[1]}/{args[2]}"
        
        # API က block မလုပ်အောင် Browser ပုံစံဖမ်းခြင်း
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        response = requests.get(full_url, headers=headers, timeout=12)
        data = response.json()

        if data.get('error') or not data.get('data'):
            bot.edit_message_text("❌ အကောင့်မတွေ့ပါ! ID နှင့် Server ပြန်စစ်ပါ။", chat_id=message.chat.id, message_id=status_msg.message_id)
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
        
    except Exception as e:
        print(f"Error: {e}") # Render Log ထဲမှာ error ကြည့်ရန်
        bot.send_message(message.chat.id, "🚫 **API မှ တုံ့ပြန်မှု မရှိပါ။** ခဏနေမှ ပြန်စမ်းကြည့်ပါ သို့မဟုတ် ID/Server မှားနေနိုင်ပါသည်။")

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
