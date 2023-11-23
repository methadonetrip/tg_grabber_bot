from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import asyncio

start = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("Работа")
b2 = KeyboardButton("Информация")
start.add(b1,b2)

info = ReplyKeyboardMarkup(resize_keyboard=True)
gods = KeyboardButton(text="Создатели")
how_it_works = KeyboardButton(text="Как я работаю?")
to_start = KeyboardButton(text="В начало")
info.add(gods, how_it_works, to_start)

back_to_info = ReplyKeyboardMarkup(resize_keyboard=True)
back_info = KeyboardButton(text="К информации")
back_to_info.add(back_info, to_start)

work = ReplyKeyboardMarkup(resize_keyboard=True)
chanels = KeyboardButton(text="Список каналов")
filters = KeyboardButton(text="Мои фильтры")
work.add(chanels, filters, to_start)

filters_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
add_filter = KeyboardButton("Добавить фильтр")
back_to_work = KeyboardButton("К работе")
filters_keyboard.add(add_filter,back_to_work,to_start)

channels_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
add_channel = KeyboardButton("Добавить канал")
channels_keyboard.add(add_channel, back_to_work, to_start)
