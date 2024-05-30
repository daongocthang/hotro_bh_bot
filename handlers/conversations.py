from handlers import commands as cmd
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

START, NEXT, END = range(3)


async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xử lý thành công.")
    return ConversationHandler.END


conv_success_handler = ConversationHandler(
    entry_points=[CommandHandler('success', cmd.default)],
    states={
        END: [
            MessageHandler(filters.TEXT, complete)
        ]
    },
    fallbacks=[CommandHandler('cancel', complete)]
)
