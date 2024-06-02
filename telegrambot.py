from telegram import Update
from telegram.ext import (Application,
                          CommandHandler,
                          ChatMemberHandler, PicklePersistence)

from handlers import commands as cmd, chat_member
from handlers.conversations import main_ch, send_result_ch
from persist.fb import FirebasePersistence
from torchbot.passport import credentials, fb_config
from utils.loader import get_logger

logger = get_logger(__name__)

# async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    # persistence = PicklePersistence(os.path.join(ROOT_DIR, "db"))
    persistence = FirebasePersistence(
        url=credentials['database_url'],
        credentials=fb_config
    )
    app = Application.builder().token(credentials['token']).persistence(persistence).build()
    # handle member joining/leaving chats
    app.add_handler(ChatMemberHandler(chat_member.greeting, ChatMemberHandler.CHAT_MEMBER))

    # errors
    # app.add_error_handler(error)

    # commands
    app.add_handler(CommandHandler(['start', 'help'], cmd.help_command))
    app.add_handler(CommandHandler('hotro_tra_ht', cmd.support_command))
    app.add_handler(CommandHandler('show', cmd.show_command))
    app.add_handler(send_result_ch)

    # conversations
    app.add_handler(main_ch)

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES,poll_interval=1)
