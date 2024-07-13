from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart
import random

user_rou = Router()


def load_cities(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]


cities_database = load_cities('city.txt')

current_city = random.choice(cities_database)
game_active = False
used_cities = []


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
    if message.chat.type != 'private' and not game_active:
        game_active = True
        current_city = random.choice(cities_database)
        used_cities = [current_city]
        await message.reply(f"Привет,{message.from_user.full_name}. Приятной игры в города.\n"
                            f"Первый город будет: {current_city}.\n"
                            f"Теперь назови город на букву '{get_last_letter(current_city)}'.\n")


@user_rou.message(Command('stop'))
async def stop_game(message: types.Message):
    global game_active, used_cities
    if game_active:
        game_active = False
        used_cities = []
        await message.reply("Игра остановлена. Спасибо за игру!", reply_markup=types.ReplyKeyboardRemove())


@user_rou.message()
async def handle_city(message: types.Message):
    global current_city, game_active, used_cities
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

        current_city = input_city
        used_cities.append(current_city)
        await message.reply(f"Верно! Введенный город '{current_city}' существует. Давай дальше! "
                            f"Теперь назови город на букву '{get_last_letter(current_city)}'.")
