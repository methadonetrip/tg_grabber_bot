from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Работа', callback_data='work'),
    InlineKeyboardButton(text='Информация', callback_data='info')
    ]
])

info = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Создатели', callback_data='gods'),
    InlineKeyboardButton(text='Как я работаю', callback_data='h_i_w'),
    InlineKeyboardButton(text='В начало', callback_data='to_start')
    ]
])

back_to_info = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='К информации', callback_data='info'),
    InlineKeyboardButton(text='В начало', callback_data='to_start')
    ]
])

work = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Мои фильтры', callback_data='my_filters'),
    InlineKeyboardButton(text='В начало', callback_data='to_start')
    ]
])

filters_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
    InlineKeyboardButton(text='Добавить фильтр', callback_data='add_filter'),
    InlineKeyboardButton(text='К работе', callback_data='work'),
    InlineKeyboardButton(text='В начало', callback_data='to_start')
    ]
])
