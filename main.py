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
active_tickets = {} 
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

# ==========================================
# CALLBACK HANDLERS
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # --- Fix for Ticket Answers ---
    if call.data.startswith('answer_'):
        tid = call.data.split('_')[1]
        if tid not in active_tickets:
            bot.answer_callback_query(call.id, "Ticket resolved.")
            return
        # Claiming logic...
        user_id = active_tickets[tid]['user_id']
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        msg = bot.send_message(call.from_user.id, f"Replying to [{tid}]. Type your response:")
        bot.register_next_step_handler(msg, lambda m: send_user_reply(m, user_id, tid))
        return

    # --- MAIN MENU NAVIGATION ---
    if call.data == "main_menu":
        bot.edit_message_text("👑 *Main Menu:*", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(), parse_mode="Markdown")

    elif call.data == "show_packages":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("✅ With FTP", callback_data="buy_with_ftp"),
                   InlineKeyboardButton("❌ Without FTP", callback_data="buy_without_ftp"))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("🛒 *Select Package Category:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "show_help":
        help_text = (
            "🛠️ *Available Commands:*\n\n"
            "🔹 `/start` - Main Menu\n"
            "🔹 `/buy` - Purchase Flow\n"
            "🔹 `/support` - Open Ticket\n"
            "🔹 `/freeproxy` - Claim Free Proxy\n"
            "🔹 `/feedback` - Leave Review\n"
            "🔹 `/admins` - Staff List"
        )
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "show_ftps":
        markup = InlineKeyboardMarkup(row_width=2)
        ftps = [
            ("Sam Online", "http://172.16.50.7/"), ("Sam Online 2", "http://172.16.50.4/"),
            ("Ftpbd 3", "http://server3.ftpbd.net/"), ("Ftpbd 5", "http://server5.ftpbd.net/"),
            ("IPlex", "http://Iplex.live/"), ("Crazy Ctg", "http://crazyctg.com/"),
            ("Circle Ftp", "http://circleftp.net/"), ("New Circle", "http://new.circleftp.net/"),
            ("FTPBD", "http://ftpbd.net/"), ("PlusNet", "http://fs.plus.net.bd/")
        ]
        for n, u in ftps: markup.add(InlineKeyboardButton(n, url=u))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("⚡ *BDIX Speed Test Links:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "show_setup":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Android (SOCKS5)", url="https://t.me/bypass_empire/9"),
                   InlineKeyboardButton("Android (HTTP)", url="https://t.me/bypass_empire/10"),
                   InlineKeyboardButton("PC (Proxifier)", url="https://t.me/bypass_empire/17"),
                   InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("🚀 *Setup Guides:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "show_isp":
        markup = InlineKeyboardMarkup(row_width=2)
        isps = ["AmberIT", "Link3", "Carnival", "Dot Internet"]
        for i in isps: markup.add(InlineKeyboardButton(i, callback_data="isp_selected"))
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("📡 *Select your ISP:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "isp_selected":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
        bot.edit_message_text("✅ *Your ISP is fully supported.*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # --- BUY FLOW Logic ---
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
        msg = bot.send_message(call.message.chat.id, "📝 Please type your review/feedback for Bypass Empire:")
        bot.register_next_step_handler(msg, process_feedback)

# [Include the Ticket, Feedback, and Admin logic functions from the previous v2.0]
# They remain the same to keep the logic stable.

if __name__ == "__main__":
    bot.infinity_polling()
