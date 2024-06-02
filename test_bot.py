from typing import Union

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from persist.fb import FirebasePersistence
from torchbot.passport import credentials, fb_config
from utils.loader import get_logger
from handlers import commands as cmd

logger = get_logger(__name__)
TOKEN = '6853378453:AAGz6n341ZR5eGrulSeLTJoHKD-O0l9rVhE'


async def default_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mention_name = update.effective_user.mention_html()
    await update.message.reply_html(f'I am a chatbot. Nice to meet {mention_name}.')


if __name__ == '__main__':
    # app = Application.builder().token(TOKEN).build()
    # app.add_handler(CommandHandler(['start', 'help'], default_command))
    #
    # # Run the bot until the user presses Ctrl-C
    # app.run_polling(allowed_updates=Update.ALL_TYPES)

    fb = FirebasePersistence(
        url=credentials['database_url'],
        credentials=fb_config
    )

    logger.info(fb.fb_user_data)
