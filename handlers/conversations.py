import os
import random
import re
from typing import Optional, Tuple

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)

from torchbot.passport import credentials
from torchbot.prediction import predict
from utils import loader, ROOT_DIR
from handlers import commands as cmd, state
from utils.emoji import Emoji

NEXT, END = range(2)

intents: dict = loader.load_yml(os.path.join(ROOT_DIR, "intents.yml"))['intents']


def handle_response(text: str) -> Optional[Tuple[None, None]]:
    text = text.strip().lower()
    prob, tag = predict(text)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.95:
        for intent in intents:
            if tag in intent['tag']:
                return random.choice(intent['responses']), intent.get('state')
    return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text_html = update.message.text_html
    text = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text_html}"')

    # Torch AI
    """
    admin_tag: str = str(credentials['admin_id'])
    bot_tag: str = credentials['bot_id']
    
    if message_type == "group":
        new_text = None        
        if bot_tag in text_html:
            new_text = text.replace(bot_tag, '')
        if admin_tag in text_html:
            matcher = re.search('<a href="tg://user\?id=' + admin_tag + '">.+?</a>', text_html)
            new_text = text_html.replace(matcher.group(), '').__str__()

        if hasattr(update.message.reply_to_message, 'from_user'):
            from_user: dict = update.message.reply_to_message.from_user.to_dict()
            if from_user.get('username') == bot_tag:
                new_text = text
        
        if new_text:
            response, action = handle_response(new_text)
        else:
            return ConversationHandler.END

    else:
    """
    response, action = handle_response(update.message.text)
    if response:
        await update.message.reply_text(response)
        return action if action else ConversationHandler.END
    else:
        return ConversationHandler.END


def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


async def _next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bạn vui lòng nhập mã bảo hành.")
    return NEXT


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("... " + Emoji.SLEEPING_FACE)


main_ch = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT | filters.COMMAND, start)],
    states={
        NEXT: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex('done$')), _next)
        ],
        ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND, timeout)]
    },
    conversation_timeout=30,
    fallbacks=[MessageHandler(filters.Regex('done$'), end)]
)

send_result_ch = ConversationHandler(
    entry_points=[CommandHandler('send', cmd.send_result)],
    states={
        state.NEXT: [
            MessageHandler(filters.Regex(r'^(Success|Failure|Cancel).+?', ), cmd.later_send),
            MessageHandler(filters.TEXT, cmd.post_send),
        ]
    },
    fallbacks=[MessageHandler(filters.Regex('(done|cancel)$'), end)]
)
