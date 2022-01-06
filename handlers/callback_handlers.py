from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.exceptions import MessageNotModified
from sqlalchemy.orm import sessionmaker
from keyboards.inline import get_photos_kb, get_photo_rating_kb
from utils.states import UserStates
from db.db_api import get_photo, get_rating_by_id, send_reaction


async def show_photo(callback_query: CallbackQuery, pool: sessionmaker, state: FSMContext):
    last_bot_photo_id = (await state.get_data(None)).get('last_message_id')
    photo_id = int(callback_query.data.split('_')[-1])
    photo_data = await get_photo(photo_id, pool)
    if last_bot_photo_id is None:
        await callback_query.message.answer_photo(photo_data,
                                                  reply_markup=
                                                  get_photo_rating_kb(await get_rating_by_id(photo_id, pool), photo_id))

    else:
        await callback_query.bot.edit_message_media(InputMediaPhoto(photo_data), callback_query.message.chat.id,
                                                    message_id=last_bot_photo_id,
                                                    reply_markup=get_photo_rating_kb(
                                                        await get_rating_by_id(photo_id, pool), photo_id))
    temp = callback_query.message.message_id + 1
    await state.update_data(last_message_id=temp)
    await callback_query.answer()


async def change_rating(callback_query: CallbackQuery, pool):
    action = callback_query.data.startswith('actionlike')
    photo_id = int(callback_query.data.split('_')[-1])
    await send_reaction(callback_query.from_user.id, int(callback_query.data.split('_')[-1]), action, pool)
    try:
        await callback_query.message.edit_reply_markup(get_photo_rating_kb(await get_rating_by_id(photo_id, pool),
                                                                           photo_id))
    except MessageNotModified:
        await callback_query.answer('Вы уже выбрали этот вариант')


async def change_page_photo(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(get_photos_kb((await state.get_data()).get('photos'),
                                                                 int(callback_query.data.split('_')[-1])))


# TODO fix when user send messages between inline kb and photo
async def exit_from_photos(callback_query: CallbackQuery, state: FSMContext):
    last_bot_photo_id = (await state.get_data(None)).get('last_message_id')
    await callback_query.message.delete()
    if last_bot_photo_id is not None:
        await callback_query.bot.delete_message(callback_query.message.chat.id,
                                                last_bot_photo_id)
    await state.finish()


async def rest_calls(*args):
    print('wrong state')


def register_callback_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(show_kb, state=UserStates.watching_photos)
    dp.register_callback_query_handler(change_rating, state=UserStates.watching_photos, text_startswith='action')
    dp.register_callback_query_handler(show_photo, state=UserStates.watching_photos, text_startswith='photo')
    dp.register_callback_query_handler(change_page_photo, state=UserStates.watching_photos, text_startswith='page')
    dp.register_callback_query_handler(exit_from_photos, state=UserStates.watching_photos, text='exit_from_photos')
    dp.register_callback_query_handler(rest_calls, state='*')
