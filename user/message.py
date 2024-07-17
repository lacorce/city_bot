from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart
from admin.keyboard.keyboard import admin_key
import random
import aiofiles
from database import database as db
from aiogram.filters import CommandObject

user_rou = Router()
game_active = False
used_cities = []
user_scores = []
current_city = None


async def initialize_bot():
    global cities_database, current_city, game_active, used_cities
    cities_file = 'city.txt'
    cities_database = await load_cities(cities_file)
    return cities_database


async def load_cities(file_path):
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            cities = [line.strip() for line in await file.readlines()]
    except FileNotFoundError:
        cities = []
    return cities


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
        await message.answer(f'Приветсвую, администратор,{message.from_user.full_name}🏙\n'
                             'Удачного дня!', reply_markup=admin_key)
    if message.chat.type != 'private' and not game_active:
        game_active = True
        cities_database = await initialize_bot()
        current_city = random.choice(cities_database)
        used_cities = [current_city]
        last = get_last_letter(current_city)
        await message.reply(f"Привет, {message.from_user.full_name}. Приятной игры в города.\n"
                            f"Первый город будет: {current_city}.\n"
                            f"Теперь назови город на букву '{last}'.\n")


@user_rou.message(Command('stop'))
async def stop_game(message: types.Message):
    global game_active, used_cities
    if message.chat.type != 'private' and game_active:
        game_active = False
        used_cities = []
    if not user_scores:
        game_status_not = "Игра остановлена. Спасибо за игру!👋"
        await message.reply(game_status_not)
    if user_scores:
        for user in user_scores:
            game_stats = "Игра остановлена. Спасибо за игру!👋\nИгроки/Баллы:\n"
            game_stats += f"👤{user['name']}: {user['score']}\n"
            first_name = user['name']
            balls = user['score']
            await db.add_statistic(first_name, balls)
        await message.reply(game_stats)


@user_rou.message(Command('statistic'))
async def show_statistic(message: types.Message):
    user_scores = await db.get_statistic()
    info = (f"Статистика игроков:\n"
            f"Игроки/Баллы:\n")
    for user in user_scores:
        info += f"👤{user[0]}: {user[1]}\n"
    await message.answer(info)


@user_rou.message(Command('add_city'))
async def cmd_settimer(
        message: types.Message,
        command: CommandObject

):
    if command.args is None:
        await message.answer(
            "Ошибка: неправильный формат команды.\n Пример:"
            "<code>/add_city 'Город'</code>", parse_mode='HTML'
        )
        return
    try:
        text_to_send = command.args.split(" ")
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_city <Город>"
        )
        return
    for user_city_application in text_to_send:
        await message.answer(
            'Заявка поданна!\n'
            f'Ваш предложанный город - {user_city_application}')
        name = user_city_application
        await db.add_application(name)


@user_rou.message()
async def handle_city(message: types.Message):
    global current_city, game_active, used_cities, user_scores
    first_name = message.from_user.first_name
    await db.add_user(first_name)
    cities_database = await load_cities('city.txt')

    if message.chat.type != 'private' and game_active:
        input_city = normalize_city_name(message.text)
        if input_city in used_cities:
            await message.reply("❌Вы уже вводили этот город. Попробуйте другой город.")
            return

        if input_city not in [normalize_city_name(city) for city in cities_database]:
            await message.reply(
                "🤔Это не город или такого города нет в базе(можете отправить свой город на модреацию с помощью комманды -/add_city."
                "Попробуй еще раз.")
            return
        last_letter = get_last_letter(current_city)
        if input_city[0].upper() != last_letter:
            await message.reply(f"❗Город должен начинаться с буквы '{last_letter}'. Попробуй еще раз.")
            return
        else:
            used_cities.append(input_city)
            current_city = input_city
            user_name = message.from_user.first_name

            user_found = False
            for user in user_scores:
                if user['name'] == user_name:
                    user['score'] += 1
                    user_found = True
                    break

            if not user_found:
                user_scores.append({'name': user_name, 'score': 1})

            await message.reply(f"✅Верно! Введенный город '{input_city}' существует. Давай дальше! "
                                f"Теперь назови город на букву '{get_last_letter(input_city)}'. ")
