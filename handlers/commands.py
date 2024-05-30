import re

from telegram import Update
from telegram.ext import ContextTypes

from utils.decorators import admin_only
from utils.emoji import Emoji


def parse_pickle(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.setdefault("codeList", {})


async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcom to Telegram Bot')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Xin chào! Tôi là bot hỗ trợ bảo hành.')


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


@admin_only
async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data: dict = parse_pickle(context)
    # await update.message.reply_text(text='\n'.join(list(data.keys())) if data else "Không có dữ liệu.")
    await update.message.reply_text(data.__str__() if data else "Không có dữ liệu.")


@admin_only
async def detail_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        'chat_id': update.message.chat_id,
        'user': update.effective_user.mention_html()
    }
    await update.message.reply_text(data.__str__())
