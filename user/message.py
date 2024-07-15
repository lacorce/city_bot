from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart
from admin.keyboard.keyboard import admin_key
import random
import aiofiles

user_rou = Router()


async def initialize_bot():
    global cities_database
    cities_file = 'city.txt'
    cities_database = await load_cities(cities_file)


async def load_cities(file_path):
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            cities = [line.strip() for line in await file.readlines()]
    except FileNotFoundError:
        cities = []
    return cities


game_active = False
used_cities = []
user_balls = {}


def get_last_letter(city):
    last_letter = city[-1]
    if last_letter in "цыь":
        return city[-2].capitalize()
    else:
        return last_letter.capitalize()


def normalize_city_name(city):
    return city.strip().capitalize()


@user_rou.message(CommandStart())
async def start_game(message: types.Message):
    global current_city, game_active, used_cities
    if message.from_user.id == 6292728634 and message.chat.type == 'private':
        await message.answer(f'Приветсвую,администратор,{message.from_user.full_name}\n'
                             'Удачного дня!', reply_markup=admin_key)
    if message.chat.type != 'private' and not game_active:
        game_active = True
        cities_database = await load_cities('city.txt')
        current_city = random.choice(cities_database)
        used_cities = [current_city]
        await message.reply(f"Привет,{message.from_user.full_name}. Приятной игры в города.\n"
                            f"Первый город будет: {current_city}.\n"
                            f"Теперь назови город на букву '{get_last_letter(current_city)}'.\n")


@user_rou.message(Command('check'))
async def check_one(message: types.Message):
    print(cities_database)
    await message.answer('123')


@user_rou.message(Command('stop'))
async def stop_game(message: types.Message):
    global game_active, used_cities
    if message.chat.type != 'private' and game_active:
        game_active = False
        used_cities = []
        await message.reply("Игра остановлена. Спасибо за игру!")
        await message.reply("Статистика игры ")


@user_rou.message()
async def handle_city(message: types.Message):
    global current_city, game_active, used_cities
    cities_database = await load_cities('city.txt')
    if message.chat.type != 'private' and game_active:
        input_city = normalize_city_name(message.text)
        if input_city in used_cities:
            await message.reply("Вы уже вводили этот город. Попробуйте другой город.")
            return

        if input_city not in [normalize_city_name(city) for city in cities_database]:
            await message.reply("Это не город или такого города нет в базе. Попробуй еще раз.")
            return

        if input_city[0].upper() != get_last_letter(current_city):
            await message.reply(f"Город должен начинаться с буквы '{get_last_letter(current_city)}'. Попробуй еще раз.")
            return

        user_id = message.from_user.id
        if user_id in user_balls:
            user_balls[user_id] += 1
        else:
            user_balls[user_id] = 1

        # Print user_id and current balls
        print(f"{user_id} balls: {user_balls[user_id]}")

        await message.reply(f"Верно! Введенный город '{current_city}' существует. Давай дальше! "
                            f"Теперь назови город на букву '{get_last_letter(current_city)}'.")
