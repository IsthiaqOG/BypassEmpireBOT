import telebot
import uuid
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Secure Token Loading
BOT_TOKEN = '8620575996:AAGFPby3Lw245MgEQEjDw4zROnugBvaHiRw'
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# ADMIN CONFIGURATION
# ==========================================
ADMIN_IDS = [6777275402, 5322548070, 5845601574, 6853501258] 

# ==========================================
# BOT STATE (In-Memory)
# ==========================================
free_proxies = []
active_tickets = {} # ticket_id: {'user_id': id, 'msg_ids': {admin_id: msg_id}}
user_ids = set()

# ==========================================
# DATA STRUCTURES
# ==========================================
PRICES = {
    "without_ftp": {
        "1": {"100Mbps": "150 TK", "50Mbps": "100 TK", "30Mbps": "80 TK", "20Mbps": "50 TK"},
        "3": {"100Mbps": "405 TK", "50Mbps": "280 TK", "30Mbps": "220 TK", "20Mbps": "135 TK"},
        "6": {"100Mbps": "850 TK", "50Mbps": "565 TK", "30Mbps": "440 TK", "20Mbps": "270 TK"},
        "12": {"100Mbps": "1750 TK", "50Mbps": "1150 TK", "30Mbps": "900 TK", "20Mbps": "550 TK"}
    },
    "with_ftp": {
        "1": {"100Mbps": "250 TK", "50Mbps": "150 TK", "30Mbps": "120 TK", "20Mbps": "80 TK"},
        "3": {"100Mbps": "700 TK", "50Mbps": "420 TK", "30Mbps": "320 TK", "20Mbps": "210 TK"},
        "6": {"100Mbps": "1400 TK", "850 TK": "850 TK", "30Mbps": "660 TK", "20Mbps": "430 TK"},
        "12": {"100Mbps": "2700 TK", "1600 TK": "1600 TK", "30Mbps": "1300 TK", "20Mbps": "900 TK"}
    }
}

# ==========================================
# KEYBOARDS
# ==========================================
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💎 View Packages", callback_data="show_packages"),
               InlineKeyboardButton("🚀 Proxy Setup", callback_data="show_setup"))
    markup.add(InlineKeyboardButton("⚡ BDIX Speed Test", callback_data="show_ftps"),
               InlineKeyboardButton("📡 Select ISP", callback_data="show_isp"))
    markup.add(InlineKeyboardButton("🛠️ Help & Commands", callback_data="show_help"),
               InlineKeyboardButton("📝 Leave Feedback", callback_data="start_feedback"))
    markup.add(InlineKeyboardButton("🏆 More Details & Prizes", url="https://t.me/bypass_empire/32"))
    return markup

# ==========================================
# USER COMMANDS
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.chat.id)
    welcome_text = (
        "👑 *Welcome to Bypass Empire Official*\n\n"
        "Premium BDIX bypass solutions for a seamless internet experience.\n"
        "Use the menu below to navigate our services."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def buy_flow_start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("✅ With FTP", callback_data="buy_with_ftp"),
               InlineKeyboardButton("❌ Without FTP", callback_data="buy_without_ftp"))
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
    bot.send_message(message.chat.id, "🛒 *Select Category:*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['support'])
def support_command(message):
    msg = bot.send_message(message.chat.id, "📞 Please type your support message or send an image with a caption to open a ticket.")
    bot.register_next_step_handler(msg, process_ticket)

@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    msg = bot.send_message(message.chat.id, "📝 Please type your review/feedback for Bypass Empire:")
    bot.register_next_step_handler(msg, process_feedback)

@bot.message_handler(commands=['freeproxy'])
def get_free_proxy(message):
    if free_proxies:
        p = free_proxies.pop(0)
        bot.send_message(message.chat.id, f"🎁 *Here is your free proxy:*\n\n`{p}`\n\nPlease use it responsibly.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Free proxies are not available right now. Please check back later.")

@bot.message_handler(commands=['admins'])
def admin_list(message):
    text = (
        "👤 *Owner & Admins:*\n"
        "• @Rocket_BD (Owner)\n"
        "• @Isthiaq_OG (Admin)\n"
        "• @AmizingTreasures (Admin)\n"
        "• @Mr_X_Mehedi (Admin)\n"
        "• @tnabil (Admin)\n\n"
        "🎖️ *Active Sub Admins:*\n"
        "• @Mubin_b (Active Sub Admin)\n"
        "• @tanvir_rahman_999 (Active Sub Admin)\n"
        "• @Joy_Roy_248 (Active Sub Admin)"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ==========================================
# ADMIN COMMANDS
# ==========================================
@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        broadcast_msg = message.text.split('/broadcast ', 1)[1]
        count = 0
        for uid in user_ids:
            try:
                bot.send_message(uid, f"📢 *Important Update:*\n\n{broadcast_msg}", parse_mode="Markdown")
                count += 1
            except: pass
        bot.reply_to(message, f"✅ Broadcast sent to {count} users.")
    except IndexError:
        bot.reply_to(message, "Usage: `/broadcast [message]`")

@bot.message_handler(commands=['addproxy'])
def add_free_proxy(message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        proxy_data = message.text.split('/addproxy ', 1)[1]
        free_proxies.append(proxy_data)
        bot.reply_to(message, "✅ Proxy successfully added to the free pool.")
    except IndexError:
        bot.reply_to(message, "Usage: `/addproxy [details]`")

# ==========================================
# TICKET SYSTEM LOGIC
# ==========================================
def process_ticket(message):
    ticket_id = str(uuid.uuid4())[:8]
    active_tickets[ticket_id] = {'user_id': message.chat.id, 'msg_ids': {}}
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔓 Answer Ticket", callback_data=f"answer_{ticket_id}"))
    ticket_header = f"🎫 *New Ticket* [{ticket_id}]\nFrom: @{message.from_user.username}\n\n"
    
    for admin in ADMIN_IDS:
        try:
            if message.content_type == 'text':
                sent = bot.send_message(admin, ticket_header + f"Msg: {message.text}", reply_markup=markup, parse_mode="Markdown")
                active_tickets[ticket_id]['msg_ids'][admin] = sent.message_id
            elif message.content_type == 'photo':
                sent = bot.send_photo(admin, message.photo[-1].file_id, caption=ticket_header + (message.caption or ""), reply_markup=markup, parse_mode="Markdown")
                active_tickets[ticket_id]['msg_ids'][admin] = sent.message_id
        except: pass
    bot.send_message(message.chat.id, "✅ Your ticket is open. An admin will respond shortly.")

def process_feedback(message):
    feedback_text = f"🌟 *New Review:*\n\nFrom: @{message.from_user.username}\nMessage: {message.text}"
    for admin in ADMIN_IDS:
        try: bot.send_message(admin, feedback_text, parse_mode="Markdown")
        except: pass
    bot.send_message(message.chat.id, "✅ Thank you! Your feedback has been sent to our team.")

# ==========================================
# CALLBACK HANDLERS
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # --- Ticket Answering ---
    if call.data.startswith('answer_'):
        tid = call.data.split('_')[1]
        if tid not in active_tickets:
            bot.answer_callback_query(call.id, "Ticket already resolved.")
            return
        for aid, mid in active_tickets[tid]['msg_ids'].items():
            if aid != call.from_user.id:
                try: bot.delete_message(aid, mid)
                except: pass
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        msg = bot.send_message(call.from_user.id, f"Replying to ticket [{tid}]. Type your response:")
        bot.register_next_step_handler(msg, lambda m: send_user_reply(m, active_tickets[tid]['user_id'], tid))
        return

    # --- Main Menu Logic ---
    if call.data == "main_menu":
        bot.edit_message_text("👑 *Main Menu:*", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(), parse_mode="Markdown")

    elif call.data == "show_help":
        help_text = "🛠️ *Commands:*\n/start, /buy, /support, /freeproxy, /feedback, /admins"
        bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu")), parse_mode="Markdown")

    elif call.data == "show_ftps":
        markup = InlineKeyboardMarkup(row_width=2)
        ftps = [("Sam Online", "http://172.16.50.7/"), ("Sam Online 2", "http://172.16.50.4/"), ("Ftpbd 3", "http://server3.ftpbd.net/"), ("IPlex", "http://Iplex.live/"), ("Circle Ftp", "http://circleftp.net/")]
        for n, u in ftps: markup.add(InlineKeyboardButton(n, url=u))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("⚡ *BDIX Speed Test:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ["buy_with_ftp", "buy_without_ftp"]:
        cat = "with_ftp" if "with_ftp" in call.data else "without_ftp"
        markup = InlineKeyboardMarkup(row_width=2)
        for d in ["1", "3", "6", "12"]: markup.add(InlineKeyboardButton(f"{d} Month", callback_data=f"dur_{cat}_{d}"))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("📅 *Select Duration:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("dur_"):
        _, cat, dur = call.data.split('_')
        markup = InlineKeyboardMarkup(row_width=2)
        for s in PRICES[cat][dur]: markup.add(InlineKeyboardButton(s, callback_data=f"pkg_{cat}_{dur}_{s}"))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text(f"🚀 *Select {dur} Month {cat.replace('_',' ').title()} Package:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("pkg_"):
        _, cat, dur, speed = call.data.split('_')
        price = PRICES[cat][dur][speed]
        bot.edit_message_text(f"✅ *Price:* {price}\n📞 To buy proxy inbox @Rocket_BD", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu")), parse_mode="Markdown")

    elif call.data == "start_feedback":
        process_feedback(call.message)

def send_user_reply(message, uid, tid):
    try:
        bot.send_message(uid, f"💬 *Admin Reply:*\n\n{message.text}", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Delivered.")
        if tid in active_tickets: del active_tickets[tid]
    except: bot.send_message(message.chat.id, "❌ User blocked bot.")

if __name__ == "__main__":
    print("Bypass Empire Bot v2.0 Live.")
    bot.infinity_polling()

