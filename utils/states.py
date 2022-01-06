from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    watching_photos = State()
    uploading_photos = State()

