from time import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from db import Database
from utils.messages import MESSAGES
from keyboards.inline import like_kb, set_btn
from data.config import (
    API_TOKEN,
    ADMIN_ID,
    DATABASE_HOST,
    DATABASE_USERNAME,
    DATABASE_PASSWORD,
    DATABASE_NAME,
    DATABASE_PORT,
)


bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
db = Database(DATABASE_HOST, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_PORT, ADMIN_ID)


@dp.callback_query_handler(text=['like', 'dislike'])
async def process_callback_button1(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    file_name = callback_query.message.caption
    is_liked = callback_query.data == 'like'
    data = callback_query.data
    if db.is_same_choose(user_id, file_name, data):
        await bot.answer_callback_query(callback_query.id)
        return
    db.change_rating(user_id, file_name, is_liked)
    db.set_file_rating(user_id, file_name, is_liked)
    likes, dislikes = db.get_rating(file_name)
    set_btn(likes, dislikes)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                        callback_query.message.message_id,
                                        reply_markup=like_kb)


@dp.message_handler(commands='start', commands_prefix='!/\\')
async def start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    is_admin = False
    if not db.is_in_db(user_id):
        db.add_user(user_id, username, first_name, is_admin)
    await bot.send_message(user_id, MESSAGES['start'])


@dp.message_handler(commands='help', commands_prefix='!/\\')
async def help_(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(user_id, MESSAGES['help'])


@dp.message_handler(commands='admin', commands_prefix='!/\\')
async def admin(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(user_id, db.is_admin(user_id))


@dp.message_handler(lambda m: m.text in db.show_avaliable())
async def send_photo(message: types.message):
    text = message.text
    photo, name = db.get_photo(text)
    likes, dislikes = db.get_rating(text)
    set_btn(likes, dislikes)
    await bot.send_photo(message.from_user.id, photo, reply_markup=like_kb, caption=name)


@dp.message_handler()
async def show_avaliable(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    current_time = message.date
    db.add_message(user_id, text, current_time)
    result = ', '.join(db.show_avaliable())
    await bot.send_message(user_id, result)


@dp.message_handler(content_types=['photo'])
async def upload_sample(message: types.Message):
    user_id = message.from_user.id
    file_name = message.caption or str(message.from_user.id) + str(time())
    file_data = message.photo[0].file_id
    db.upload_sample(file_name, file_data, user_id)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def main():
    db.connect()
    executor.start_polling(dp, on_shutdown=shutdown)


if __name__ == '__main__':
    main()
