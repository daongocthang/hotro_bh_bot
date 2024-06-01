import re
from typing import NamedTuple

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, Sticker
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from handlers import state
from utils.decorators import admin_only
from utils.emoji import Emoji

result_ok: bool


class DataInput(NamedTuple):
    chat_id: int
    mention: str
    message_id: int


def parse_pickle(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data


def parse_bool(b: bool) -> int:
    return 1 if b else 0


async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcom to Telegram Bot')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Xin chào! Tôi là bot hỗ trợ bảo hành.')


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pattern = re.compile(r'^TNBH[0-9]{7}$')
    try:
        code = context.args[0]
        code = code.strip()
        if pattern.match(code):
            print(code)
            parse_pickle(context)[code.strip()] = DataInput(
                chat_id=update.message.chat_id,
                mention=update.effective_user.mention_html(),
                message_id=update.message.id
            )
            await update.message.reply_text(f'{Emoji.OK_HAND} Bạn chờ BHKV xử lý nhé!')
        else:
            await update.message.reply_text(f'Mã bảo hành không đúng {Emoji.NO_ENTRY}')
    except (IndexError, ValueError):
        await update.message.reply_text(f'Không có mã bảo hành {Emoji.DISAPPOINT_FACE}')


@admin_only
async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data: dict = parse_pickle(context)
    print(data)
    await update.message.reply_text(text='\n'.join(list(data.keys())) if data else "Không có dữ liệu.")
    # await update.message.reply_text(data.__str__() if data else "Không có dữ liệu.")


@admin_only
async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = [
        ["Success - đã xong"],
        ["Failure - không tìm thấy"],
        ["Cancel - hủy bỏ"]
    ]
    # await update.message.reply_text('Vui lòng nhập danh sách mã bảo hành')
    reply_markup = ReplyKeyboardMarkup(choice, one_time_keyboard=True)
    await update.message.reply_text('Những trường hợp này như thế nào?!', reply_markup=reply_markup)
    return state.NEXT


async def later_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global result_ok

    text = update.message.text
    text = text.lower()
    if 'cancel' in text:
        await update.message.reply_text('Không còn gì để làm... ' + Emoji.SLEEPING_FACE)
        return ConversationHandler.END

    result_ok = 'success' in text

    await update.message.reply_text('Vui lòng nhập danh sách mã bảo hành', reply_markup=ReplyKeyboardRemove())
    return state.NEXT


async def post_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tickets = update.message.text.split('\n')
    data = parse_pickle(context)
    reply_text = [
        '%s chưa tiếp nhận hoặc đang chờ CM. %s hỏi lại CH nha!',
        '%s đã trả CM. %s lh CH để xác nhận nhé!'
    ]

    for key in tickets:
        if key in data:
            user: DataInput = data.pop(key)
            mention_html = user.mention
            await context.bot.send_message(
                chat_id=user.chat_id,
                reply_to_message_id=user.message_id,
                text=reply_text[parse_bool(result_ok)] % (key, mention_html),
                parse_mode=ParseMode.HTML
            )

            await update.message.reply_html(f'{key} đã gửi đến {mention_html}')
        else:
            await update.message.reply_text(f'{key} không có trong danh sách chờ xử lý')

    return ConversationHandler.END


@admin_only
async def detail_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        'chat_id': update.message.chat_id,
        'user': update.effective_user.mention_html()
    }
    await update.message.reply_text(data.__str__())
