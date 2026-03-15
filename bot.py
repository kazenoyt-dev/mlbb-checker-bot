import telebot
import requests
from flask import Flask
import threading
import os
import re
from telebot import types

TOKEN = '7955125092:AAEWZFwKGwCCBaoMXl_t4wChYlhSnRE6lEg'
bot = telebot.TeleBot(TOKEN)
API_URL = 'https://magic-mall-mlbb-id-check-v1.hlaaunghtun68.workers.dev/mobile-legends'

# 🌍 နိုင်ငံအလိုက် အလံများ သတ်မှတ်ပေးခြင်း
REGION_MAP = {
    "MM": "Myanmar 🇲🇲", "TH": "Thailand 🇹🇭", "ID": "Indonesia 🇮🇩",
    "SG": "Singapore 🇸🇬", "PH": "Philippines 🇵🇭", "KH": "Cambodia 🇰🇭",
    "MY": "Malaysia 🇲🇾", "VN": "Vietnam 🇻🇳", "BR": "Brazil 🇧🇷",
    "US": "United States 🇺🇸", "RU": "Russia 🇷🇺", "TR": "Turkey 🇹🇷"
}

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
    bot.reply_to(message, "👋 **MLBB Checker မှ ကြိုဆိုပါတယ်!**\n\nစစ်ရန်: `/check 178178059(2911)` လို့ ရိုက်စစ်နိုင်ပါပြီ။", parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def handle_check(message):
    # စာကြောင်းထဲမှ ဂဏန်းများကိုသာ သီးသန့်ရွေးထုတ်ခြင်း
    numbers = re.findall(r'\d+', message.text)
    
    # ဂဏန်း ၂ ခု မပြည့်လျှင်
    if len(numbers) < 2:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါသည်။\nဥပမာ: `/check 1609968597(16765)` သို့မဟုတ် `/check 1609968597 16765`", parse_mode="Markdown")
        return
    
    game_id = numbers[0]
    server_id = numbers[1]
    
    status_msg = bot.reply_to(message, "🔍 စစ်ဆေးနေပါသည်...")
    data = fetch_mlbb_data(game_id, server_id)
    
    if not data or data.get('error') or not data.get('data'):
        bot.edit_message_text("❌ အကောင့်မတွေ့ပါ! ID နှင့် Server ပြန်စစ်ပါ။", chat_id=message.chat.id, message_id=status_msg.message_id)
        return

    info = data['data']
    
    # နိုင်ငံကုဒ်ကို အလံနှင့် ပြောင်းလဲခြင်း
    region_code = info.get('region', 'Unknown').upper()
    region_display = REGION_MAP.get(region_code, f"{region_code} 🌍")

    res = f"🦁 **MLBB Info**\n━━━━━━━━━━━━━━\n👤 IGN: `{info.get('username')}`\n🌍 Region: {region_display}\n🆔 ID: `{game_id} ({server_id})`\n"
    
    if info.get('shop_events'):
        res += "\n💎 **2x Status:**\n"
        for event in info['shop_events']:
            for item in event.get('goods', []):
                status = "🔴 မရတော့ပါ" if item.get('reached_limit') else "🟢 ရနိုင်ပါသေးသည်"
                res += f"• {item.get('title')} — {status}\n"
    
    bot.edit_message_text(res, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

# --- Inline Query Handler ---
# ဂဏန်း ၂ ခုပါမှသာ အလုပ်လုပ်မည်
@bot.inline_handler(lambda query: len(re.findall(r'\d+', query.query)) >= 2)
def query_text(inline_query):
    try:
        numbers = re.findall(r'\d+', inline_query.query)
        game_id = numbers[0]
        server_id = numbers[1]
        
        data = fetch_mlbb_data(game_id, server_id)
        
        if not data or data.get('error') or not data.get('data'):
            return

        info = data['data']
        region_code = info.get('region', 'Unknown').upper()
        region_display = REGION_MAP.get(region_code, f"{region_code} 🌍")

        res = f"🎯 **MLBB Account Info**\n👤 IGN: `{info.get('username')}`\n🆔 ID: `{game_id} ({server_id})`\n🌍 Region: {region_display}\n"
        
        if info.get('shop_events'):
            res += "\n💎 **2x Status:**\n"
            for event in info['shop_events']:
                for item in event.get('goods', []):
                    status = "🔴 မရတော့ပါ" if item.get('reached_limit') else "🟢 ရနိုင်ပါသေးသည်"
                    res += f"• {item.get('title')} — {status}\n"

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
