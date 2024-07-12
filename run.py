import asyncio
from aiogram import Bot, Dispatcher
from user.message import user_rou

bot = Bot(token="7239116420:AAFVMkpjlPt61eIi-8izbzG3JSZoUagYL7Q")
dp = Dispatcher()

async def start():
    dp.include_router(user_rou)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
