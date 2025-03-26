from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from flask import Flask
from threading import Thread

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7564277215:AAEqGt1594LRufXmZCkuQQwkia3-0__rMZo'
TARGET_USER_ID = 7733415587  # Sruthi
YOUR_USER_ID = 1906584261    # You

# ---------- Flask Server ----------
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------

# Create the Application object globally so we can access its job queue
app = Application.builder().token(TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == TARGET_USER_ID:
        await update.message.reply_text("Hi! Someone wanted me to reach out. How can I assist you?")
        await context.bot.send_message(chat_id=YOUR_USER_ID, text="She has started the bot! You can now send messages.")
    elif user_id == YOUR_USER_ID:
        await update.message.reply_text("Bot started! Use /send to message her.")
    else:
        await update.message.reply_text("This bot is for a private purpose.")

# /send command
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == YOUR_USER_ID:
        message_text = " ".join(context.args)
        if message_text:
            await update.message.reply_text("Trying to send your message... Will keep trying until she starts the bot.")
            # Use global app.job_queue instead of context.job_queue
            app.job_queue.run_repeating(
                try_send_message,
                interval=60,
                first=0,
                data={"chat_id": TARGET_USER_ID, "text": message_text, "update": update},
                name=f"send_to_{TARGET_USER_ID}"
            )
        else:
            await update.message.reply_text("Usage: /send <message>")
    else:
        await update.message.reply_text("Only my creator can use this command!")

# Scheduled message job
async def try_send_message(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    text = job.data["text"]
    update = job.data["update"]
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
        await update.message.reply_text(f"Message sent to user {chat_id}: {text}")
        job.schedule_removal()
    except Exception as e:
        logger.error(f"Failed to send to {chat_id}: {str(e)}")
        if "chat not found" in str(e).lower() or "forbidden" in str(e).lower():
            pass

# Echo handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == TARGET_USER_ID:
        await update.message.reply_text(f"You said: {update.message.text}")
    elif user_id == YOUR_USER_ID:
        await update.message.reply_text("She hasn’t replied yet. Try /send again.")
    else:
        await update.message.reply_text("This bot isn’t for you!")

# Main function
def main():
    keep_alive()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
