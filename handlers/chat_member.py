import logging
import random
from typing import Optional, Tuple

from telegram import ChatMemberUpdated, Update, ChatMember
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from utils.emoji import Emoji

logger = logging.getLogger(__name__)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get('status')
    is_old_member, is_new_member = chat_member_update.difference().get('is_member', (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR
    ] or (old_status == ChatMember.RESTRICTED and is_old_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR
    ] or (new_status == ChatMember.RESTRICTED and is_new_member is True)

    return was_member, is_member


async def greeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    joining = not was_member and is_member
    # leaving = was_member and not is_member

    if joining:
        emoji_list = [Emoji.PARTY_POPPER, Emoji.PARTYING_FACE, Emoji.CONFETTI_BALL]

        await update.effective_chat.send_message(random.choice(emoji_list))

        text = f'Chào mừng {member_name} đã tham gia nhóm.'
        if member_name != cause_name:
            text += f'\nCảm ơn {cause_name} đã mời {member_name}.'

        await update.effective_chat.send_message(text, parse_mode=ParseMode.HTML)
