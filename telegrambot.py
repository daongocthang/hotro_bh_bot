import os
from typing import List
import logging

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, PicklePersistence

from torchbot import utils
from torchbot.prediction import predict

TOKEN = '7196696529:AAG78sEoFvYUdpxncpYuHyDVF8zfpLtqxz4'
BOT_USERNAME = '@hotro_bh_bot'

basedir = os.path.dirname(os.path.abspath(__file__))
intents = utils.load_yml(os.path.join(basedir, "intents.yml"))['intents']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Commands
def parse_pickle(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.setdefault("codeList", {})


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/hotro_tra_ht <mã bảo hành> - để được hỗ trợ trả hệ thống, không nhận thiết bị vật lý')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a Helpbot. Please type something so I cam respond.')


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command.')


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = context.args[0]
    if code.startswith("TNBH"):
        parse_pickle(context)[update.message.chat_id] = context.args[0]
        await update.message.reply_text(f'BHKV đã xử lý mã bảo hành {code} sau hh:mm')
    else:
        await update.message.reply_text(f'Mã bảo hành không hợp lệ. Bạn vui lòng nhập lại mã bảo hành.')


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = parse_pickle(context)
    await update.message.reply_text(data if data else "Không có dữ liệu.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # TODO: do in background

    text = text.strip().lower()
    prob, tag = predict(text)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.95 and tag == "tra_he_thong":
        await update.message.reply_text(
            'Bạn vui lòng nhắn /hotro_tra_ht <MA BAO HANH>'
        )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def handle_send(text: str, chat_id: str):
    bot = telegram.Bot(token=TOKEN)
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)


if __name__ == '__main__':
    persistence = PicklePersistence(os.path.join(basedir, "db"))
    app = Application.builder().token(TOKEN).persistence(persistence).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('show', show_command))
    app.add_handler(CommandHandler('hotro_tra_ht', support_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # errors
    # app.add_error_handler(error)

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=3)
