import asyncio
from aiogram import Bot, Dispatcher
from user.message import user_rou
from admin.callback.callback import call
from admin.message.message import a_mess
from aiogram.types import BotCommand


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="Начать игру"),
        BotCommand(command="/stop", description="Закончить игру"),
        BotCommand(command="/add_city", description="Подать заявление на добавление города")
    ]
    await bot.set_my_commands(bot_commands)
bot = Bot(token="7239116420:AAFVMkpjlPt61eIi-8izbzG3JSZoUagYL7Q")
dp = Dispatcher()

async def start():
    await setup_bot_commands()
    dp.include_router(a_mess)
    dp.include_router(call)
    dp.include_router(user_rou)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
