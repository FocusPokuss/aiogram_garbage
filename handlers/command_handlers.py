from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from keyboards.inline import get_photos_kb
from utils.states import UserStates
from db.db_api import add_user, get_available


async def watch_photos(message: Message, pool: sessionmaker, state: FSMContext):
    photos = await get_available(pool)
    await state.update_data(photos=photos)
    await UserStates.watching_photos.set()
    await message.bot.send_message(message.from_user.id, 'Вот что у нас есть:',
                                   reply_markup=get_photos_kb(photos))


async def reset_state(message: Message, state: FSMContext):
    await message.answer(f'Ваш state ресетнут')
    await state.finish()


async def start_uploading_photos(message: Message):
    await UserStates.uploading_photos.set()
    await message.answer('Можете подгрузить карточки')


async def start(message: Message, pool: sessionmaker):
    try:
        await add_user(message.from_user.id, message.from_user.first_name, pool)
        await message.answer('Добро пожаловать\nЕсли хотите посмотреть карточки напишите /photo')
    except IntegrityError:
        await message.answer('Вы уже бывали тут...')


def register_command_handlers(dp: Dispatcher):
    dp.register_message_handler(watch_photos, state=None, commands='photo')
    dp.register_message_handler(reset_state, state='*', commands='reset')
    dp.register_message_handler(start_uploading_photos, state=None, commands='upload', is_admin=True)
    dp.register_message_handler(start, state=None, commands='start')
