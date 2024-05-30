import functools
import logging

from telegram import Update

from torchbot.passport import credentials

logger = logging.getLogger(__name__)


def admin_only(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            update: Update
            for a in args:
                if isinstance(a, Update):
                    update = a
                    break

            if not update:
                raise TypeError('Argument update is not found.')

            if update.message.chat_id != credentials['admin_id']:
                raise PermissionError('Only allow chatting with admin')
            return await func(*args, **kwargs)
        except (TypeError, PermissionError) as e:
            logger.error(e)

    return wrapper
