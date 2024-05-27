import os

import telegram

from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update

import random
from torchbot import utils
from torchbot.prediction import predict

TOKEN = '7196696529:AAG78sEoFvYUdpxncpYuHyDVF8zfpLtqxz4'
BOT_USERNAME = '@hotro_bh_bot'

basedir = os.path.dirname(os.path.abspath(__file__))
intents = utils.load_yml(os.path.join(basedir, "intents.yml"))['intents']


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me. I am Helpbot.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a Helpbot. Please type something so I cam respond.')


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command.')


# Responses
def handle_response(text: str) -> str:
    sentence: str = text.lower()

    prob, tag = predict(sentence)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.9:
        for intent in intents:
            if tag in intent['tag']:
                return random.choice(intent['responses'])

    return 'I do not understand what you wrote...'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # TODO: do in background

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def handle_send(text: str, chat_id: str):
    bot = telegram.Bot(token=TOKEN)
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # errors
    app.add_error_handler(error)

    # polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
