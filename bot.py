import telebot
import requests
from flask import Flask
import threading
import os
from telebot import types

TOKEN = '7955125092:AAEWZFwKGwCCBaoMXl_t4wChYlhSnRE6lEg'
bot = telebot.TeleBot(TOKEN)
API_URL = 'https://magic-mall-mlbb-id-check-v1.hlaaunghtun68.workers.dev/mobile-legends'

app = Flask(__name__)

@app.route('/')
def home(): return "Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Common Function for API Call ---
def fetch_mlbb_data(game_id, server_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Origin': 'https://htunhlaaung.github.io',
        'Referer': 'https://htunhlaaung.github.io/'
    }
    try:
        response = requests.get(f"{API_URL}/{game_id}/{server_id}", headers=headers, timeout=15)
        return response.json()
    except:
        return None

# --- Command Handler ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 **MLBB Checker Inline Mode ရပါပြီ!**\n\nဘယ်နေရာမှာမဆို `@BotUsername ID Server` လို့ ရိုက်ပြီး စစ်နိုင်ပါပြီ။", parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def handle_check(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ ပုံစံ: `/check 1609968597 16765`")
        return
    
    status_msg = bot.reply_to(message, "🔍 စစ်ဆေးနေပါသည်...")
    data = fetch_mlbb_data(args[1], args[2])
    
    if not data or data.get('error') or not data.get('data'):
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

# --- Inline Query Handler (Mention ခေါ်ပြီး စစ်သည့်အပိုင်း) ---
@bot.inline_handler(lambda query: len(query.query.split()) == 2)
def query_text(inline_query):
    try:
        game_id, server_id = inline_query.query.split()
        data = fetch_mlbb_data(game_id, server_id)
        
        if not data or data.get('error') or not data.get('data'):
            return

        info = data['data']
        res = f"🎯 **MLBB Account Info**\n👤 IGN: `{info.get('username')}`\n🆔 ID: `{game_id} ({server_id})`\n🌍 Region: {info.get('region')}\n"
        
        if info.get('shop_events'):
            res += "\n💎 **2x Status:**\n"
            for event in info['shop_events']:
                for item in event.get('goods', []):
                    status = "🔴 မရတော့ပါ" if item.get('reached_limit') else "🟢 ရနိုင်ပါသေးသည်"
                    res += f"• {item.get('title')} — {status}\n"

        # Result ကို ကတ်ပြားပုံစံ ပြသခြင်း
        r = types.InlineQueryResultArticle(
            '1',
            f"စစ်ဆေးပြီးပြီ: {info.get('username')}",
            types.InputTextMessageContent(res, parse_mode="Markdown"),
            description=f"ID: {game_id} ({server_id}) ၏ 2x Status ကို ကြည့်ရန် နှိပ်ပါ။"
        )
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
