from aiogram import Dispatcher, executor, Bot, types
from settings import TOKEN_API
import texts, keyboards
import asyncio

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

#Старт
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=texts.START_TEXT,
                           reply_markup=keyboards.start)
    await message.delete()

#Старт -> Информация
@dp.message_handler(text="Информация")
async def info_command(message: types.Message):
    await message.answer(text=texts.INFO_TEXT,
                         reply_markup=keyboards.info)
    await message.delete()

#Старт -> Информация -> Создатели
@dp.message_handler(text="Создатели")
async def info_gods_command(message: types.Message):
    await message.answer(text=texts.GODS_TEXT,
                         reply_markup=keyboards.back_to_info)
    await message.delete()

#Создатели/Как я работаю? -> Информация
@dp.message_handler(text="К информации")
async def to_info_command(message: types.Message):
    await message.answer(text=texts.INFO_TEXT,
                         reply_markup=keyboards.info)
    await message.delete()

#Старт -> Информация -> Как я работаю?
@dp.message_handler(text="Как я работаю?")
async def info_gods_command(message: types.Message):
    await message.answer(text=texts.H_I_W,
                         reply_markup=keyboards.back_to_info)
    await message.delete()

#Старт -> Работа
@dp.message_handler(text="Работа")
async def work_command(message: types.Message):
    await message.answer(text=texts.WORK_TEXT,
                         reply_markup=keyboards.work)
    await message.delete()

#Старт -> Работа -> Мои фильтры
@dp.message_handler(text="Мои фильтры")
async def work_filter_command(message: types.Message):
    await message.answer(text=texts.FIlTERS_TEXT,
                         reply_markup=keyboards.filters_keyboard)
    await message.delete()

#Старт -> Работа -> Список каналов
@dp.message_handler(text="Список каналов")
async def work_command(message: types.Message):
    await message.answer(text=texts.CHANNELS_TEXT,
                         reply_markup=keyboards.channels_keyboard)
    await message.delete()

#Список каналов/Мои фильтры -> Работа
@dp.message_handler(text="К работе")
async def to_info_command(message: types.Message):
    await message.answer(text=texts.WORK_TEXT,
                         reply_markup=keyboards.work)
    await message.delete()


#Информация/Работа -> Старт
@dp.message_handler(text="В начало")
async def to_start_command(message: types.Message):
    await message.answer(text=texts.START_TEXT,
                         reply_markup=keyboards.start)
    await message.delete()

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True)

