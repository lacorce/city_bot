from aiogram import Router , F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup

call = Router()

class City(StatesGroup):
    new_city = State()

@call.callback_query(F.data == 'add_city')
async def add_city(call: types.CallbackQuery,state : FSMContext):
    await state.set_state(City.new_city)
    print('1')
    await call.message.answer(text="Введите название города:")
    print('2')




