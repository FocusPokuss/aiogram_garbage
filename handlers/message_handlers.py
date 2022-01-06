from aiogram import Dispatcher
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from utils.states import UserStates
from sqlalchemy.orm import sessionmaker
from db.db_api import add_photo


async def upload_photo(message: Message, pool: sessionmaker):
    title = message.caption
    if not title:
        await message.answer('Нет названия, повторите попытку')
    else:
        title = title.strip()
        try:
            await add_photo(user_id=message.from_user.id, data=message.photo[-1].file_id,
                            t_upload=message.date, title=title, pool=pool)
            await message.answer(f'{title} добавлен в коллекцию')
        except IntegrityError:
            await message.answer(f'{title} уже есть в коллекции')


async def echo(message: Message):
    await message.answer(message.text + '\nЕсли хотите посмотреть карточки напишите /photo')


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(upload_photo, state=UserStates.uploading_photos, content_types='photo')
    dp.register_message_handler(echo, state=None)


