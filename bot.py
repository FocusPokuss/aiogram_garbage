import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.base import Base
from middlewares.db import DbPoolMiddleware
from middlewares.role import RoleMiddleware
from handlers.message_handlers import register_message_handlers
from handlers.command_handlers import register_command_handlers
from handlers.callback_handlers import register_callback_handlers
from utils.filters import AdminFilter, RoleFilter
from config import (
    DATABASE_HOST,
    DATABASE_USERNAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_NAME,
    API_TOKEN,
    ADMIN_ID,
)


async def main():
    # creating engine and and session instances
    async_engine = create_async_engine(
        f'postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}',
        max_overflow=-1, pool_size=20)
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # creating bot and dispatcher instances
    bot = Bot(API_TOKEN)
    dp = Dispatcher(bot, storage=RedisStorage2())

    # setup middlewares
    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(DbPoolMiddleware(async_session))
    dp.middleware.setup(RoleMiddleware(ADMIN_ID))

    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    # registrating handlers
    register_command_handlers(dp)
    register_callback_handlers(dp)
    register_message_handlers(dp)

    # start polling
    try:
        logging.info('start polling')
        print('Start polling!')
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        # since asyncio.run() bugged on Windows we explicitly find and run loop
        asyncio.get_event_loop_policy().get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        print('Bot stopped!')
