import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Your BotFather Token
TOKEN = "8925413219:AAGKTdmzX5-MZ3rw8ft1VSy" + "HdAbWHXXDnvs"

# Your personal Telegram numeric ID
DEVELOPER_CHAT_ID = 722127665  

# Define conversation states
CHOOSING, TYPING_MESSAGE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("💬 Customer Support", callback_data="support")],
        [InlineKeyboardButton("⚠️ Complaint / App Malfunction", callback_data="complaint")],
        [InlineKeyboardButton("🐛 Report an Issue / Bug", callback_data="bug")],
        [InlineKeyboardButton("👨‍💻 Contact Developers", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Welcome to SMSGuard Support! 🛡️\n\n"
        "How can we help you today? Please choose an option below:"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    category_map = {
        "support": "Customer Support",
        "complaint": "Complaint / App Malfunction",
        "bug": "Issue / Bug Report",
        "contact": "Developer Contact Message"
    }
    
    selected_category = category_map.get(query.data, "General Inquiry")
    context.user_data["category"] = selected_category
    
    await query.message.edit_text(
        f"You selected: {selected_category}.\n\n"
        "Please type and send your message/details below. Our development team will review it and respond!",
        parse_mode="Markdown"
    )
    return TYPING_MESSAGE

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_message = update.message.text
    category = context.user_data.get("category", "General")
    
    dev_notification = (
        f"🚨 New SMSGuard Ticket Received!\n\n"
        f"📂 Category: {category}\n"
        f"👤 From: {user.full_name} (@{user.username or 'No username'}, ID: {user.id})\n\n"
        f"📝 Message:\n{user_message}"
    )
    
    try:
        await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=dev_notification, parse_mode="Markdown")
    except Exception as e:
        print(f"Failed to notify developer: {e}")
    
    await update.message.reply_text(
        "✅ Thank you! Your message has been sent to the SMSGuard developers. We will get back to you soon.",
        parse_mode="Markdown"
    )
    
    return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Session cancelled. Type /start to open the menu again.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_handler)],
            TYPING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    print("Bot is running...")
    application.run_polling()

# Start the bot
main()