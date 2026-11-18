import telebot
import json
import os

# আপনার সঠিক বটের টোকেন
TOKEN = '9066302895:AAF6qnTRWRmgFOlABxZBrQa25u9gVfX8F50'

# আপনার চ্যানেল আইডি
CHANNEL_ID = "@viralvideo7885"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'database.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return {"links": {}, "users": []}
    return {"links": {}, "users": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Sub check error: {e}")
    return False

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    data = load_data()
    
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
    
    text = message.text
    if len(text.split()) > 1:
        payload = text.split()[1]
        if payload.startswith("link_"):
            link_id = payload.replace("link_", "")
            
            if check_subscription(user_id):
                links = data.get("links", {})
                if link_id in links:
                    original_url = links[link_id]
                    
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton("🔗 আসল লিংকে প্রবেশ করুন", url=original_url))
                    markup.add(telebot.types.InlineKeyboardButton("📤 চ্যানেলটি শেয়ার করুন", url=f"https://t.me/share/url?url=https://t.me/{CHANNEL_ID.replace('@','')}"))
                    
                    bot.send_message(
                        message.chat.id, 
                        "✅ **ভেরিফিকেশন সফল হয়েছে!**\n\nনিচের বাটনে ক্লিক করে লিংকে প্রবেশ করুন:", 
                        reply_markup=markup, 
                        parse_mode="Markdown"
                    )
                else:
                    bot.send_message(message.chat.id, "⚠️ এই লিংকটি পাওয়া যায়নি বা মেয়াদ শেষ হয়ে গেছে।")
            else:
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("📢 ১. প্রথমে চ্যানেলে জয়েন করুন", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
                
                share_url = f"https://t.me/share/url?url=https://t.me/{CHANNEL_ID.replace('@','')}&text=ভাই, এই দারুণ চ্যানেলে জয়েন করো! এখানে জোস জোস লিংক পাওয়া যায়:"
                markup.add(telebot.types.InlineKeyboardButton("📤 ২. চ্যানেলটি অন্য কাউকে শেয়ার করুন", url=share_url))
                markup.add(telebot.types.InlineKeyboardButton("🔄 ৩. ভেরিফাই করুন", callback_data=f"verify_{link_id}"))
                
                bot.send_message(
                    message.chat.id, 
                    "❌ **লিংক আনলক করতে হলে শর্ত পূরণ করতে হবে!**\n\n১. প্রথমে আমাদের চ্যানেলে জয়েন করুন।\n২. আমাদের চ্যানেলের লিংকটি শেয়ার করুন।\n৩. এরপর **'ভেরিফাই করুন'** বাটনে ক্লিক করুন।", 
                    reply_markup=markup, 
                    parse_mode="Markdown"
                )
            return

    bot.send_message(message.chat.id, "👋 স্বাগতম! যেকোনো লিংক লক করতে আমাদের বট ব্যবহার করুন।\n\nযেকোনো লিংক বটে পাঠান, আমি সেটির একটি সুরক্ষিত লিংক তৈরি করে দেবো।")

@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def create_locker_link(message):
    original_url = message.text.strip()
    data = load_data()
    
    link_id = str(len(data.get("links", {})) + 1)
    
    if "links" not in data:
        data["links"] = {}
        
    data["links"][link_id] = original_url
    save_data(data)
    
    bot_info = bot.get_me()
    bot_username = bot_info.username
    
    locked_link = f"https://t.me/{bot_username}?start=link_{link_id}"
    
    bot.reply_to(
        message, 
        f"🔒 **আপনার লিংক লক করা হয়েছে!**\n\nনিচের লিংকটি এখন আপনি আপনার চ্যানেলে শেয়ার করতে পারেন:\n`{locked_link}`", 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_"))
def callback_verify(call):
    user_id = call.from_user.id
    link_id = call.data.replace("verify_", "")
    
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ ভেরিফিকেশন সফল হয়েছে!", show_alert=True)
        
        data = load_data()
        links = data.get("links", {})
        if link_id in links:
            original_url = links[link_id]
            
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🔗 আসল লিংকে প্রবেশ করুন", url=original_url))
            markup.add(telebot.types.InlineKeyboardButton("📤 চ্যানেলটি শেয়ার করুন", url=f"https://t.me/share/url?url=https://t.me/{CHANNEL_ID.replace('@','')}"))
            
            bot.edit_message_text(
                "✅ **সব শর্ত পূরণ হয়েছে!**\n\nএখন নিচের বাটনে ক্লিক করে লিংকে প্রবেশ করতে পারেন:", 
                call.message.chat.id, 
                call.message.message_id, 
                reply_markup=markup, 
                parse_mode="Markdown"
            )
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন করেননি! আগে চ্যানেলে জয়েন করুন।", show_alert=True)

print("Link Locker Bot is running...")
bot.infinity_polling()
              
