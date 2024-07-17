from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from admin.keyboard.keyboard import create_kb_list_cities, application_city
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import aiofiles
from database import database as db

call = Router()


class City(StatesGroup):
    new_city = State()
    add_city_txt = State()
    user = State()


async def initialize_bot():
    global cities_database
    cities_file = 'city.txt'
    cities_database = await load_cities(cities_file)


async def load_cities(file_path='city.txt'):
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            cities = [line.strip() for line in await file.readlines()]
    except FileNotFoundError:
        cities = []
    return cities


async def save_cities(cities, file_path='city.txt'):
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
        for city in cities:
            await file.write(city + '\n')


@call.callback_query(lambda call: call.data.startswith('add_city'))
async def add_city(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(City.new_city)
    await call.message.answer("💬Пожалуйста, введите название города")


@call.callback_query(lambda call: call.data == 'applications_city')
async def show_applications(call: types.CallbackQuery):
    page_number = 1
    app_city_kb = await application_city(page_number)
    await call.answer()
    await call.message.answer('📄Все заявки на добавление городов:', reply_markup=app_city_kb)


@call.callback_query(lambda call: call.data == 'send_txt')
async def send_txt(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(City.add_city_txt)
    close_send_txt = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="↩️", callback_data=f"back_admin_menu")
            ]
        ]
    )
    await call.message.answer('Пожалуйста, отправьте файл в формате txt.📄', reply_markup=close_send_txt)


@call.callback_query(lambda call: call.data == 'cities_list')
async def show_cities_list(call: types.CallbackQuery):
    await initialize_bot()
    if cities_database:
        page_number = 1
        list_markup = await create_kb_list_cities(cities_database, page_number)
        await call.answer()
        await call.message.answer('📃Список городов', reply_markup=list_markup)
    else:
        await call.message.answer('⚪️Список городов пуст.')


@call.callback_query(lambda call: call.data.startswith('page_'))
async def paginate_cities(call: types.CallbackQuery):
    page_number = int(call.data.split('_')[1])
    per_page = 5
    list_markup = await create_kb_list_cities(cities_database, page_number, per_page)
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=list_markup)


@call.callback_query(lambda call: call.data.startswith('apppage_'))
async def paginate_cities(call: types.CallbackQuery):
    page_number = int(call.data.split('_')[1])
    per_page = 5
    list_markup = await application_city(page_number, per_page)
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=list_markup)


@call.callback_query(lambda call: call.data.startswith('appcity_'))
async def paginate_cities(call: types.CallbackQuery):
    app_edit_city = call.data.split('_')[1]
    id = app_edit_city
    result = await db.check_app(id)
    await call.answer()
    edit_kb_app = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(text='🗑Удалить', callback_data=f'deleteapp_{app_edit_city}'),
                InlineKeyboardButton(text='✅Принять', callback_data=f'acceptapp_{app_edit_city}'),
                InlineKeyboardButton(text="↩️", callback_data=f"back_admin_menu")
            ]
        ]
    )
    await call.answer()
    await call.message.edit_text(f'Вы выбрали город {result[1]}.', reply_markup=edit_kb_app)


@call.callback_query(lambda call: call.data.startswith('acceptapp'))
async def accept_application(call: types.CallbackQuery):
    id = call.data.split('_')[1]
    result = await db.check_app(id)
    result_check = result[1]
    cities = await load_cities()

    if result_check in cities:
        await call.message.answer(f"❌Город '{result_check}' уже существует в списке.")
        await db.delete_application(id)
    else:
        cities.append(result_check)
        await save_cities(cities)
        await call.message.answer(f"✅Город <b>'{result_check}'</b> успешно добавлен в список.", parse_mode='HTML')
        await db.delete_application(id)


@call.callback_query(lambda call: call.data.startswith('deleteapp_'))
async def delete_application(call: types.CallbackQuery):
    id = call.data.split('_')[1]
    result = await db.check_app(id)
    result_check = result[1]
    await db.delete_application(id)
    await call.message.answer(f' Заявка на удаление города <b>{result_check}</b> удалена.', parse_mode='HTML')


@call.callback_query(lambda call: call.data.startswith('city_'))
async def handle_city_callback(call: types.CallbackQuery):
    city_name = call.data.split('_')[1]

    edit_kb = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(text='🗑Удалить', callback_data=f'delete_{city_name}'),
                InlineKeyboardButton(text='📑Изменить', callback_data=f'edit_{city_name}'),
                InlineKeyboardButton(text="↩️", callback_data=f"back_edit_admin_menu")
            ]
        ]
    )

    await call.answer()
    await call.message.edit_text(f'Вы выбрали город {city_name}.', reply_markup=edit_kb)


@call.callback_query(lambda call: call.data.startswith(('delete_', 'edit_')))
async def handle_city_action(call: types.CallbackQuery):
    global cities_database

    action, city_name = call.data.split('_')

    if action == 'delete':
        cities_database.remove(city_name)
        await save_cities('city.txt', cities_database)
        await call.message.answer(f'✅Город {city_name} удален.')

    elif action == 'edit':
        await call.message.answer(f'Функция изменения города {city_name} пока не реализована.')

    page_number = 1
    list_markup = await create_kb_list_cities(cities_database, page_number)
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=list_markup)


@call.callback_query(F.data == 'back_admin_menu')
async def back_admin_menu(call: types.CallbackQuery):
    await call.message.delete()


@call.callback_query(F.data == 'back_edit_admin_menu')
async def back_admin_menu(call: types.CallbackQuery):
    await initialize_bot()
    if cities_database:
        page_number = 1
        list_markup = await create_kb_list_cities(cities_database, page_number)
        await call.answer()
        await call.message.edit_text('📃Список городов', reply_markup=list_markup)
