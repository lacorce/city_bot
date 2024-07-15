from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from admin.keyboard.keyboard import create_kb_list_cities
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiofiles

call = Router()


class City(StatesGroup):
    new_city = State()
    add_city_txt = State()


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


async def save_cities(file_path, cities):
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
        for city in cities:
            await file.write(city + '\n')


@call.callback_query(lambda call: call.data.startswith('add_city'))
async def add_city(call: types.CallbackQuery):
    await call.message.answer("Введите название города:")


@call.callback_query(lambda call: call.data == 'applications_city')
async def show_applications(call: types.CallbackQuery):
    await call.message.answer('Все заявки на добавление городов:')


@call.callback_query(lambda call: call.data == 'send_txt')
async def send_txt(call: types.CallbackQuery):
    await call.message.answer('Пожалуйста, отправьте файл в формате txt.')


@call.callback_query(lambda call: call.data == 'cities_list')
async def show_cities_list(call: types.CallbackQuery):
    await initialize_bot()
    if cities_database:
        page_number = 1
        list_markup = await create_kb_list_cities(cities_database, page_number)
        await call.message.answer('Список городов:', reply_markup=list_markup)
    else:
        await call.message.answer('Список городов пуст.')


@call.callback_query(lambda call: call.data.startswith('page_'))
async def paginate_cities(call: types.CallbackQuery):
    page_number = int(call.data.split('_')[1])
    per_page = 5
    list_markup = await create_kb_list_cities(cities_database, page_number, per_page)
    await call.message.edit_reply_markup(reply_markup=list_markup)


@call.callback_query(lambda call: call.data.startswith('city_'))
async def handle_city_callback(call: types.CallbackQuery):
    city_name = call.data.split('_')[1]

    edit_kb = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(text='Удалить', callback_data=f'delete_{city_name}'),
                InlineKeyboardButton(text='Изменить', callback_data=f'edit_{city_name}')
            ]
        ]
    )

    # Send a message indicating the selected city and display keyboard
    await call.message.answer(f'Вы выбрали город {city_name}.', reply_markup=edit_kb)


@call.callback_query(lambda call: call.data.startswith(('delete_', 'edit_')))
async def handle_city_action(call: types.CallbackQuery):
    global cities_database

    action, city_name = call.data.split('_')

    if action == 'delete':
        cities_database.remove(city_name)
        await save_cities('city.txt', cities_database)
        await call.message.answer(f'Город {city_name} удален.')

    elif action == 'edit':
        await call.message.answer(f'Функция изменения города {city_name} пока не реализована.')

    # Update the list after action
    page_number = 1
    list_markup = await create_kb_list_cities(cities_database, page_number)
    await call.message.edit_reply_markup(reply_markup=list_markup)
