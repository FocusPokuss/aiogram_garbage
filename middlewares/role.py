from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from utils.roles import Role


class RoleMiddleware(BaseMiddleware):

    def __init__(self, admin_id: int):
        super().__init__()
        self.admin_id = admin_id

    async def on_pre_process_message(self, message: Message, data):
        if message.from_user.id == self.admin_id:
            data['role'] = Role.ADMIN
        elif message.from_user.id:
            data['role'] = Role.USER
        else:
            data['role'] = None

    @staticmethod
    async def on_post_process_message(message: Message, _, data):
        del data['role']
