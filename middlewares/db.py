from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware


class DbPoolMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def on_process_message(self, *args):
        args[-1]['pool'] = self.pool

    async def on_process_callback_query(self, *args):
        args[-1]['pool'] = self.pool
