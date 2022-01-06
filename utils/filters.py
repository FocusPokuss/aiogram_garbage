from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message
from utils.roles import Role


class RoleFilter(BoundFilter):
    key = 'role'

    def __init__(self, role=None):
        if role is None:
            self.roles = None
        elif isinstance(role, Role):
            self.roles = {role}
        else:
            self.roles = set(role)

    async def check(self, message: Message):
        if self.roles is None:
            return True
        data = ctx_data.get()
        return data.get("role") in self.roles


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin=None):
        self.is_admin = is_admin

    async def check(self, message: Message):
        if self.is_admin is None:
            return True
        data = ctx_data.get()
        return (data.get("role") is Role.ADMIN) == self.is_admin


