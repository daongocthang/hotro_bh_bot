from ast import literal_eval
from collections import defaultdict
from copy import deepcopy
from typing import Dict, Any

import firebase_admin
from firebase_admin import db
from firebase_admin.db import Reference
from telegram.ext import BasePersistence, PersistenceInput


class FirebasePersistence(BasePersistence):
    def __init__(self, url: str, credentials: dict, store_user_data=True, store_chat_data=True, store_bot_data=True):
        super().__init__(
            store_data=PersistenceInput(
                store_bot_data,
                store_chat_data,
                store_user_data
            )
        )
        cred = firebase_admin.credentials.Certificate(credentials)
        firebase_admin.initialize_app(cred, {'databaseURL': url})
        self.fb_user_data = db.reference('user_data')
        self.fb_chat_data = db.reference('chat_data')
        self.fb_bot_data = db.reference('bot_data')
        self.fb_conversation = db.reference('conversation_data')

    @staticmethod
    def convert_key(data: Dict) -> Dict:
        output = {}
        for k, v in data.items():
            if k.isdigit():
                output[int(k)] = v
            else:
                output[k] = v
        return output

    @staticmethod
    def get(ref: Reference) -> Dict[int, Any]:
        output = FirebasePersistence.convert_key(ref.get() or {})
        return output

    async def get_user_data(self):
        user_data = deepcopy(self.get(self.fb_user_data))
        return user_data

    async def get_chat_data(self):
        chat_data = deepcopy(self.get(self.fb_chat_data))
        return chat_data

    async def get_bot_data(self):
        return deepcopy(self.fb_bot_data.get() or {})

    async def get_conversations(self, name: str):
        res = self.fb_conversation.child(name).get() or {}
        return {literal_eval(k): v for k, v in res.items()}

    async def update_user_data(self, user_id: int, data: dict):
        if data:
            self.fb_user_data.child(str(user_id)).update(data)
        else:
            self.fb_user_data.child(str(user_id)).delete()

    async def update_chat_data(self, chat_id: int, data: dict):
        if data:
            self.fb_chat_data.child(str(chat_id)).update(data)
        else:
            self.fb_chat_data.child(str(chat_id)).delete()

    async def update_bot_data(self, data):
        self.fb_bot_data = data

    async def update_conversation(self, name, key, new_state):
        if new_state:
            self.fb_conversation.child(name).child(str(key)).set(new_state)
        else:
            self.fb_conversation.child(name).child(str(key)).delete()

    async def update_callback_data(self, data):
        pass

    async def get_callback_data(self):
        pass

    async def drop_chat_data(self, chat_id: int):
        self.fb_user_data.child(str(chat_id)).delete()

    async def drop_user_data(self, user_id: int):
        self.fb_user_data.child(str(user_id)).delete()

    async def refresh_bot_data(self, bot_data):
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data):
        pass

    async def refresh_user_data(self, user_id: int, user_data):
        pass

    async def flush(self):
        pass
