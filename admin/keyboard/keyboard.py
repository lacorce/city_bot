from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiofiles
from database import database as db

admin_key = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📑Добавить город", callback_data="add_city")
        ],
        [
            InlineKeyboardButton(text="🗒Список всех городов", callback_data="cities_list")
        ],
        [
            InlineKeyboardButton(text='📝Заявки на добавление городов', callback_data='applications_city')
        ],
        [
            InlineKeyboardButton(text="📩Загрузить список городов", callback_data="send_txt")
        ]
    ]
)


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


async def create_kb_list_cities(cities_database, page_number, per_page=5):
    start_index = (page_number - 1) * per_page
    end_index = start_index + per_page
    cities_slice = cities_database[start_index:end_index]

    buttons = []
    for city in cities_slice:
        buttons.append(
            InlineKeyboardButton(text=city, callback_data=f"city_{city}")
        )

    navigation_buttons = []
    if page_number > 1:
        navigation_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"page_{page_number - 1}")
        )
    if end_index < len(cities_database):
        navigation_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"page_{page_number + 1}")
        )
    navigation_buttons.append(
        InlineKeyboardButton(text="↩️", callback_data=f"back_admin_menu")
    )
    buttons.extend(navigation_buttons)

    list_cities = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return list_cities


async def application_city(page_number, per_page=5):
    start_index = (page_number - 1) * per_page
    end_index = start_index + per_page
    applications = await db.send_application()
    cities_slice = applications[start_index:end_index]
    cities_database = applications
    buttons = []
    for city in cities_slice:
        app_city = city[1]
        call_city = city[0]
        buttons.append(
            InlineKeyboardButton(
                text=str(app_city),
                callback_data=f"appcity_{call_city}"
            )
        )
    navigation_buttons = []
    if page_number > 1:
        navigation_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"apppage_{page_number - 1}")
        )
    if end_index < len(cities_database):
        navigation_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"apppage_{page_number + 1}")
        )
    navigation_buttons.append(
        InlineKeyboardButton(text="↩️", callback_data=f"back_admin_menu")
    )
    buttons.extend(navigation_buttons)

    list_cities = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return list_cities