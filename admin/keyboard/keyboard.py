from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

admin_key = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить город", callback_data="add_city")
        ],
        [
            InlineKeyboardButton(text="Удалить город", callback_data="delete_city")
        ],
        [
            InlineKeyboardButton(text="Список городов", callback_data="cities_list")
        ],
        [
            InlineKeyboardButton(text='Заявки на добавление городов',callback_data='applications_city')
        ]
    ]
)