from aiogram import types , Router
from aiogram.fsm.context import FSMContext
from admin.callback.callback import City
a_mess = Router()

@a_mess.message(City.new_city)
async def add_city_fsm(message : types.Message,state : FSMContext):
    print('3')
    await state.update_data(new_city=message.text)
    data = await state.get_data()
    city = data['new_city']
    print(f"Новый город: {city}")  # Выводим название города в консоль

    # Сбрасываем состояние пользователя
    await state.clear()

    await message.answer(f"Город '{city}' успешно добавлен!")