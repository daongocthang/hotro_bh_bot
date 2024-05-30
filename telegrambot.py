import os
import re
from typing import Dict
import random
import logging

import telegram
from telegram import Update
from telegram.ext import (Application,
                          CommandHandler,
                          MessageHandler,
                          ContextTypes,
                          filters,
                          PicklePersistence
                          )

from utils import load
from torchbot.prediction import predict
from torchbot.passport import credentials
from utils.emoji import Emoji

basedir = os.path.dirname(os.path.abspath(__file__))
intents = load.yml(os.path.join(basedir, "intents.yml"))['intents']

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


async def detail_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data: Dict[str, str] = {
        'chat_id': update.message.chat_id,
        'user': update.effective_user.mention_html()
    }
    await update.message.reply_text(data.__str__())


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pattern = re.compile(r'TNBH[0-9]{7}')
    try:
        code = context.args[0]
        if pattern.match(code.strip()):
            parse_pickle(context)[context.args[0]] = {
                'chat_id': update.message.chat_id,
                'user': update.effective_user.mention_html()
            }

            await update.message.reply_text(f'{Emoji.OK_HAND} BHKV sẽ trả mã {code} sau hh:mm')
        else:
            await update.message.reply_text(f'Mã bảo hành không đúng {Emoji.NO_ENTRY}')
    except (IndexError, ValueError):
        await update.message.reply_text(f'Không có mã bảo hành {Emoji.DISAPPOINT_FACE}')


# Only Admin
def require_admin(update: Update):
    if update.message.chat_id != credentials['admin_id']:
        raise PermissionError("Only allow admins")


async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        require_admin(update)

        data: dict = parse_pickle(context)
        await update.message.reply_text(text='\n'.join(list(data.keys())) if data else "Không có dữ liệu.")
    except PermissionError as e:
        logger.error(e)


async def ok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    param = context.args[0]
    if param == 'true':
        pass
    if param == 'false':
        pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # TODO: do in background

    text = text.strip().lower()
    prob, tag = predict(text)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.95:
        for intent in intents:
            if tag in intent['tag']:
                await update.message.reply_text(
                    random.choice(intent['responses'])
                )
                break


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def handle_send(text: str, chat_id: str):
    bot = telegram.Bot(token=credentials['token'])
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)


if __name__ == '__main__':
    persistence = PicklePersistence(os.path.join(basedir, "db"))
    app = Application.builder().token(credentials['token']).persistence(persistence).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('show', show_command))
    app.add_handler(CommandHandler('detail_info', detail_info))

    app.add_handler(CommandHandler('hotro_tra_ht', support_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # errors
    # app.add_error_handler(error)

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=3)
