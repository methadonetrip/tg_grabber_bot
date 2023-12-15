from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery
import keyboards
import texts

api_id = ''
api_hash = ''
token = ''

client = Client(name='grabbot',api_id=api_id, api_hash=api_hash, bot_token=token)

# Старт
async def start_command(client: Client, message: Message):
    await client.send_message(chat_id=message.from_user.id,
                              text=texts.START_TEXT,
                              reply_markup=keyboards.start)

#Старт -> Информация
async def info_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.INFO_TEXT,
                                 reply_markup=keyboards.info)

#Старт -> Информация -> Создатели
async def info_gods_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.GODS_TEXT,
                                 reply_markup=keyboards.back_to_info)


#Старт -> Информация -> Как я работаю?
async def hiw_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.H_I_W,
                                 reply_markup=keyboards.back_to_info)

#Информация/Работа -> Старт
async def to_start_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.START_TEXT,
                                 reply_markup=keyboards.start)

#Старт -> Работа
async def to_work_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.WORK_TEXT,
                                 reply_markup=keyboards.work)

#Старт -> Работа -> Мои фильтры
async def to_filters_command(client: Client, call: CallbackQuery):
    await call.edit_message_text(text=texts.FIlTERS_TEXT,
                                 reply_markup=keyboards.filters_keyboard)


def call_data(data):
    async def filter_data(self, __, call: CallbackQuery):
        return self.data == call.data

    return filters.create(filter_data, data=data)

client.add_handler(MessageHandler(start_command, filters.command(commands='start')))
client.add_handler(CallbackQueryHandler(info_command, call_data('info')))
client.add_handler(CallbackQueryHandler(info_gods_command, call_data('gods')))
client.add_handler(CallbackQueryHandler(hiw_command, call_data('h_i_w')))
client.add_handler(CallbackQueryHandler(to_start_command, call_data('to_start')))
client.add_handler(CallbackQueryHandler(to_work_command, call_data('work')))
client.add_handler(CallbackQueryHandler(to_filters_command, call_data('my_filters')))

client.run()
