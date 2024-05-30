import logging
import os
import random
import re

import telegram
from telegram import Update
from telegram.ext import (Application,
                          CommandHandler,
                          MessageHandler,
                          ContextTypes,
                          filters,
                          PicklePersistence
                          )

from torchbot.passport import credentials
from torchbot.prediction import predict
from utils import load
from handlers import commands as cmd

basedir = os.path.dirname(os.path.abspath(__file__))
intents = load.yml(os.path.join(basedir, "intents.yml"))['intents']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Response
def handle_response(text: str) -> str:
    text = text.strip().lower()
    prob, tag = predict(text)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.95:
        for intent in intents:
            if tag in intent['tag']:
                return random.choice(intent['responses'])
    return 'Vẫn chưa hiểu ý bạn?!'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text_html = update.message.text_html

    print(f'User ({update.message.chat.id}) in {message_type}: "{text_html}"')

    # Torch AI processing
    admin_tag: str = str(credentials['admin_id'])
    bot_tag: str = '@' + credentials['bot_id']

    if message_type == "group":
        new_text = None
        if bot_tag in text_html:
            new_text = text_html.replace(bot_tag, '')
        if admin_tag in text_html:
            matcher = re.search('<a href="tg://user\?id=' + admin_tag + '">.+?</a>', text_html)
            new_text = text_html.replace(matcher.group(), '').__str__()

        if new_text:
            response = handle_response(new_text)
        else:
            return

    else:
        response = handle_response(update.message.text)

    await update.message.reply_text(response)


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
    app.add_handler(CommandHandler('start', cmd.start_command))
    app.add_handler(CommandHandler('hotro_tra_ht', cmd.support_command))
    app.add_handler(CommandHandler('show', cmd.show_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.Command, handle_message))

    # errors
    # app.add_error_handler(error)

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=3)
