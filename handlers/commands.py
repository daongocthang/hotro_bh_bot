import logging
import re
from collections import defaultdict
from typing import NamedTuple

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from handlers import state
from utils.decorators import admin_only
from utils.emoji import Emoji

result_ok: bool

logger = logging.getLogger(__name__)


class DataInput(NamedTuple):
    chat_id: int
    mention: str
    message_id: int


def find_user_id(s):
    patt = r'id=(.*)"'
    found = re.search(patt, s)
    if found:
        return found.group(1)


def parser_data(context: ContextTypes.DEFAULT_TYPE):
    output = {}
    for data in context.application.user_data.values():
        for k, v in data.items():
            output[k] = DataInput(*v)
    return defaultdict(dict, output)


def remove_data(user_id: int, key: str, context: ContextTypes.DEFAULT_TYPE):
    context.application.user_data.get(user_id).pop(key)
    if user_id not in context.application.user_data.keys():
        context.application.persistence.drop_user_data(user_id)
    else:
        data_changed: dict = context.application.user_data
        context.application.persistence.update_user_data(user_id, data_changed)


def parse_bool(b: bool) -> int:
    return 1 if b else 0


async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcom to Telegram Bot')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    if message_type == 'private':
        mention_name = update.message.chat.mention_html()
        text = f'Tôi có thể hộ trợ trả hệ thống bảo hành. '
        text += f'Để được hỗ trợ nhiều hơn, {mention_name} vui lòng tham gia nhóm <a href="https://t.me/+AlE4kevmxlM5OWRl">Hỗ trợ Bảo hành</a>'
        await update.message.reply_html(text)
    elif message_type == 'group':
        text = '/hotro_tra_ht <MA BAO HANH> - hỗ trợ trả hệ thống không chuyển thiết bị vật lý'
        await update.message.reply_text(text)


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data = context.user_data
        pattern = re.compile(r'^TNBH[0-9]{7}$')
        ticket = context.args[0]
        ticket = ticket.strip()
        if pattern.match(ticket):
            if ticket not in user_data:
                user_data[ticket] = DataInput(
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
    data: dict = parser_data(context)
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
    data = parser_data(context)
    reply_text = [
        '%s chưa có trên Hệ thống BH. %s bảo CH tiếp nhận trước nha!',
        '%s đã trả CM. %s lh CH để xác nhận nhé!'
    ]

    for key in tickets:
        if key in data.keys():
            user: DataInput = data.pop(key)
            user_id = find_user_id(user.mention)
            remove_data(int(user_id), key, context)
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
async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Vui lòng nhập danh sách mã bảo hành')
    return state.NEXT


async def do_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tickets = update.message.text.split('\n')
    data = parser_data(context)
    for key in tickets:
        if key in data.keys():
            user: DataInput = data.pop(key)
            user_id = find_user_id(user.mention)
            remove_data(int(user_id), key, context)
    await update.message.reply_text('Mã bảo hành đã xóa thành công.')
    return ConversationHandler.END


@admin_only
async def detail_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        'chat_id': update.message.chat_id,
        'user': update.effective_user.mention_html()
    }
    await update.message.reply_text(data.__str__())
