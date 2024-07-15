from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from admin.callback.callback import City
from aiogram.enums import ContentType

a_mess = Router()

cities_file = 'city.txt'


async def load_cities():
    try:
        with open(cities_file, 'r', encoding='utf-8') as f:
            cities = [line.strip() for line in f]
    except FileNotFoundError:
        cities = []
    return cities


async def save_cities(cities):
    with open(cities_file, 'w', encoding='utf-8') as f:
        for city in cities:
            f.write(city + '\n')


@a_mess.message(City.new_city)
async def add_city_fsm(message: types.Message, state: FSMContext):
    new_city = message.text.strip()
    print(new_city)
    if not new_city:
        await message.answer("Пожалуйста, введите название города.")
        return

    cities = await load_cities()

    if new_city in cities:
        await message.answer(f"Город '{new_city}' уже существует в списке.")
    else:
        cities.append(new_city)
        await save_cities(cities)
        await message.answer(f"Город '{new_city}' успешно добавлен в список.")

    await state.clear()


@a_mess.message(City.add_city_txt)
async def process_txt_file(message: types.Message, state: FSMContext):
    if message.document.mime_type != 'text/plain':
        await message.answer('Пожалуйста, отправьте файл в формате txt.')
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    try:

        downloaded_file = await message.bot.download_file(file_path)


        with open('file.txt', 'wb') as new_file:
            new_file.write(downloaded_file.read())


        with open('file.txt', 'r', encoding='utf-8') as f:
            new_cities = [line.strip() for line in f]

        existing_cities = await load_cities()

        added_cities = []
        for city in new_cities:
            if city not in existing_cities:
                existing_cities.append(city)
                added_cities.append(city)

        await save_cities(existing_cities)

        if added_cities:
            added_cities_text = "\n".join(f"• {city}" for city in added_cities)
            response = f"Добавлены новые города:\n{added_cities_text}"
        else:
            response = "Новые города не были добавлены, так как они уже существуют в списке."

        await message.answer(response)

    except Exception as e:
        await message.answer(f'Ошибка при обработке файла: {str(e)}')

    finally:
        await state.clear()
