import telebot
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Insert your bot token here
BOT_TOKEN = '8620575996:AAGFPby3Lw245MgEQEjDw4zROnugBvaHiRw'
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# ADMIN CONFIGURATION
# Add the Telegram numerical User IDs of your admins here.
# NOTE: These must be numerical IDs (e.g., 123456789), NOT @usernames.
# ==========================================
ADMIN_IDS = [6777275402, 5322548070, 5845601574, 6853501258] 

# ==========================================
# BOT STATE (Stored in memory)
# ==========================================
free_proxies = []
active_tickets = {} # Stores ticket_id: {'user_id': id, 'msg_ids': {admin_id: msg_id}}
user_ids = set() # Stores user IDs for the broadcast feature

# ==========================================
# PACKAGE DATA
# ==========================================
PACKAGES_WITHOUT_FTP = """
[ Packages Without FTP ]

1 Month:
100Mbps - 150 TK
50Mbps - 100 TK
30Mbps - 80 TK
20Mbps - 50 TK

3 Months:
100Mbps - 405 TK
50Mbps - 280 TK
30Mbps - 220 TK
20Mbps - 135 TK

6 Months:
100Mbps - 850 TK
50Mbps - 565 TK
30Mbps - 440 TK
20Mbps - 270 TK

12 Months:
100Mbps - 1750 TK
50Mbps - 1150 TK
30Mbps - 900 TK
20Mbps - 550 TK

* Note: 3, 6, and 12-month packages include special discounts.
"""

PACKAGES_WITH_FTP = """
[ Packages With Famous FTP (Discovery/Sam/Circle/ICC/FTPBD) ]

1 Month:
100Mbps - 250 TK
50Mbps - 150 TK
30Mbps - 120 TK
20Mbps - 80 TK

3 Months:
100Mbps - 700 TK
50Mbps - 420 TK
30Mbps - 320 TK
20Mbps - 210 TK

6 Months:
100Mbps - 1400 TK
50Mbps - 850 TK
30Mbps - 660 TK
20Mbps - 430 TK

12 Months:
100Mbps - 2700 TK
50Mbps - 1600 TK
30Mbps - 1300 TK
20Mbps - 900 TK

* Note: 3, 6, and 12-month packages include special discounts.
"""

# ==========================================
# MAIN MENU BUILDER
# ==========================================
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_packages = InlineKeyboardButton("View Proxy Packages", callback_data="show_packages")
    btn_setup = InlineKeyboardButton("Proxy Setup Guides", callback_data="show_setup")
    btn_isp = InlineKeyboardButton("Select ISP", callback_data="show_isp")
    btn_details = InlineKeyboardButton("More Details & Prizes", url="https://t.me/bypass_empire/32")
    markup.add(btn_packages, btn_setup)
    markup.add(btn_isp)
    markup.add(btn_details)
    return markup

# ==========================================
# USER COMMANDS
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.chat.id) # Save user for broadcast functionality
    welcome_text = (
        "Welcome to the official Bypass Empire bot.\n\n"
        "We provide premium BDIX bypass proxies to optimize your connection. "
        "Please select an option below or use the available commands to navigate."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Available Commands:\n"
        "/start - Access the main menu\n"
        "/buy - Purchase premium proxies\n"
        "/support - Open a support ticket\n"
        "/freeproxy - Claim a free proxy\n"
        "/admins - View the administrative team"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['buy'])
def buy_command(message):
    buy_text = (
        "To purchase premium proxies, please contact our official sales representative.\n\n"
        "Inbox: @Rocket_BD"
    )
    bot.send_message(message.chat.id, buy_text)

@bot.message_handler(commands=['admins'])
def admin_list_command(message):
    admin_text = (
        "Owner and Admins:\n"
        "@Rocket_BD (Owner)\n"
        "@Isthiaq_OG (Admin)\n"
        "@AmizingTreasures (Admin)\n"
        "@Mr_X_Mehedi (Admin)\n"
        "@tnabil (Admin)\n\n"
        "Active Sub Admins:\n"
        "@Mubin_b (Active Sub Admin)\n"
        "@tanvir_rahman_999 (Active Sub Admin)\n"
        "@Joy_Roy_248 (Active Sub Admin)"
    )
    bot.send_message(message.chat.id, admin_text)

@bot.message_handler(commands=['freeproxy'])
def get_free_proxy(message):
    if free_proxies:
        p = free_proxies.pop(0)
        bot.send_message(message.chat.id, f"Here is your free proxy:\n\n{p}\n\nPlease use it responsibly.")
    else:
        bot.send_message(message.chat.id, "Free proxies are not available right now. Please check back later.")

# ==========================================
# ADMIN COMMANDS
# ==========================================
@bot.message_handler(commands=['addproxy'])
def add_free_proxy(message):
    if message.from_user.id not in ADMIN_IDS:
        return # Silently ignore unauthorized users
    try:
        proxy_data = message.text.split('/addproxy ', 1)[1]
        free_proxies.append(proxy_data)
        bot.reply_to(message, "Proxy successfully added to the free distribution pool.")
    except IndexError:
        bot.reply_to(message, "Formatting error. Please use: /addproxy [proxy details]")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return # Silently ignores non-admins to keep it professional
    
    try:
        broadcast_message = message.text.split('/broadcast ', 1)[1]
        success_count = 0
        
        bot.reply_to(message, "Broadcast initialized. Sending to all registered users...")
        
        for uid in user_ids:
            try:
                bot.send_message(uid, f"📢 Broadcast from Admin:\n\n{broadcast_message}")
                success_count += 1
            except Exception:
                pass # Skip users who blocked the bot
                
        bot.send_message(message.chat.id, f"Broadcast complete. Successfully delivered to {success_count} users.")
    except IndexError:
        bot.reply_to(message, "Formatting error. Please use: /broadcast [your message here]")

# ==========================================
# TICKET SYSTEM LOGIC
# ==========================================
@bot.message_handler(commands=['support'])
def support_command(message):
    msg = bot.send_message(message.chat.id, "Please type your support message or send an image with a caption to open a ticket.")
    bot.register_next_step_handler(msg, process_ticket)

def process_ticket(message):
    if not ADMIN_IDS:
        bot.send_message(message.chat.id, "The support system is currently unavailable. No admins are configured.")
        return

    ticket_id = str(uuid.uuid4())[:8]
    active_tickets[ticket_id] = {'user_id': message.chat.id, 'msg_ids': {}}
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Answer Ticket", callback_data=f"answer_{ticket_id}"))
    
    ticket_header = f"New Support Ticket [{ticket_id}]\nFrom: {message.from_user.first_name} (@{message.from_user.username})\n\n"
    
    for admin in ADMIN_IDS:
        try:
            if message.content_type == 'text':
                sent_msg = bot.send_message(admin, ticket_header + f"Message:\n{message.text}", reply_markup=markup)
                active_tickets[ticket_id]['msg_ids'][admin] = sent_msg.message_id
            elif message.content_type == 'photo':
                caption = message.caption if message.caption else "No caption provided."
                sent_msg = bot.send_photo(admin, message.photo[-1].file_id, caption=ticket_header + f"Caption:\n{caption}", reply_markup=markup)
                active_tickets[ticket_id]['msg_ids'][admin] = sent_msg.message_id
        except Exception:
            pass # Skips if admin has blocked the bot or ID is invalid
            
    bot.send_message(message.chat.id, "Your support ticket has been submitted. Our team will review it shortly.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
def handle_ticket_answer(call):
    ticket_id = call.data.split('_')[1]
    
    if ticket_id not in active_tickets:
        bot.answer_callback_query(call.id, "This ticket has already been claimed or no longer exists.")
        return
        
    # Delete the ticket message from all other admins to prevent confusion
    for admin_id, msg_id in active_tickets[ticket_id]['msg_ids'].items():
        if admin_id != call.from_user.id:
            try:
                bot.delete_message(admin_id, msg_id)
            except Exception:
                pass
                
    # Remove the inline button for the admin who claimed it
    bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
    
    user_id = active_tickets[ticket_id]['user_id']
    msg = bot.send_message(call.from_user.id, f"You have claimed ticket [{ticket_id}]. Please type your response to the user:")
    bot.register_next_step_handler(msg, send_user_reply, user_id, ticket_id)
    
def send_user_reply(message, user_id, ticket_id):
    try:
        reply_text = f"Support Team Reply:\n\n{message.text}"
        bot.send_message(user_id, reply_text)
        bot.send_message(message.chat.id, "Your response has been successfully delivered to the user.")
        if ticket_id in active_tickets:
            del active_tickets[ticket_id] # Clean up the resolved ticket
    except Exception:
        bot.send_message(message.chat.id, "Failed to deliver the message. The user may have blocked the bot.")

# ==========================================
# INLINE BUTTON CALLBACK HANDLERS
# ==========================================
@bot.callback_query_handler(func=lambda call: not call.data.startswith('answer_'))
def handle_query(call):
    if call.data == "show_packages":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("With FTP", callback_data="pkg_with_ftp"),
                   InlineKeyboardButton("Without FTP", callback_data="pkg_without_ftp"))
        markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text("Please select a package category:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "pkg_with_ftp":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Back to Packages", callback_data="show_packages"))
        bot.edit_message_text(PACKAGES_WITH_FTP, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "pkg_without_ftp":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Back to Packages", callback_data="show_packages"))
        bot.edit_message_text(PACKAGES_WITHOUT_FTP, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "show_setup":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Android Setup (SOCKS5)", url="https://t.me/bypass_empire/9"),
                   InlineKeyboardButton("Android Setup (HTTP)", url="https://t.me/bypass_empire/10"),
                   InlineKeyboardButton("PC Setup (Proxifier)", url="https://t.me/bypass_empire/17"),
                   InlineKeyboardButton("Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text("Select the appropriate setup guide:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "show_isp":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("AmberIT", callback_data="isp_selected"),
                   InlineKeyboardButton("Link3", callback_data="isp_selected"),
                   InlineKeyboardButton("Carnival", callback_data="isp_selected"),
                   InlineKeyboardButton("Dot Internet", callback_data="isp_selected"))
        markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text("Please select your ISP to verify compatibility:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "isp_selected":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Back to Main Menu", callback_data="main_menu"))
        bot.edit_message_text("Your ISP is fully supported. You may proceed to view our packages.", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "main_menu":
        bot.edit_message_text("Main Menu:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

if __name__ == "__main__":
    print("Bypass Empire Professional Bot Initialization Complete.")
    bot.infinity_polling()

