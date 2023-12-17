#pip install nltk pymorphy2 pyrogram
import re
import pymysql
import json
import nltk
import pymorphy2
import asyncio
import pymysql.cursors

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer

from db import add_user_to_db, add_channel_to_db, add_user_status, read_status_info, read_channels_info, add_keyword_to_db, read_keywords_info, add_payment_to_db, read_sub_info, find_chat_id_by_payment_id
from yookassa_integration import YooKassaIntegration
from config import host, user, password, db_name, bot_token, api_id, api_hash
lemmatizer = WordNetLemmatizer()
morph = MorphAnalyzer()

api_id = api_id     # Замените на ваш Telegram API ID
api_hash = api_hash # Замените на ваш Telegram API Hash
bot_token = '6776409787:AAEOHAIOpKMdTK9dFhQVJRLB09c3lqd5-HQ'
app = Client("grabber_bot", api_id=api_id, api_hash=api_hash)

# Команда для запуска бота
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("Bot is running. Use the keyboard below:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    chat_id = message.chat.id
    await add_user_to_db(chat_id)

#НОРМАЛИЗАЦИЯ СЛОВ
def normalize_word(word, language):
    if language == 'english':
        return lemmatizer.lemmatize(word.lower())
    elif language == 'russian':
        return morph.parse(word)[0].normal_form
    else:
        return word

def read_config():
    with open('config.json', 'r') as file:
        return json.load(file)
def write_config(data):
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

# Определение пользовательской клавиатуры
keyboard = [
    [KeyboardButton('/subscribe'), KeyboardButton('/unsubscribe'), KeyboardButton('/list')],
    [KeyboardButton('/add_channel'), KeyboardButton('/add_keyword')],
    [KeyboardButton('/remove_channel'), KeyboardButton('/remove_keyword')]
]
    
@app.on_message(filters.command("add_channel") & filters.private)
async def add_channel(client, message: Message):
    user_id = message.from_user.id
    await add_user_status(1, user_id)
    await message.reply("Please send me the name/names of the channel/channels.\n Format: @channel1;@channel2")

"""try:
        channel = message.text.split(' ', 1)[1]
        config_data = read_config()
        if channel not in config_data['channels']:
            config_data['channels'].append(channel)
            write_config(config_data)
            await message.reply(f"Channel {channel} added successfully.")
        else:
            await message.reply(f"Channel {channel} is already in the list.")
    except IndexError:
        await message.reply("Please provide a channel name after the command.")"""

# УБРАТЬ КАНАЛ
@app.on_message(filters.command("remove_channel"))
async def remove_channel(client, message: Message):
    user_id = message.from_user.id
    await add_user_status(-1, user_id)
    await message.reply("Write channel")

# ПАДПИСАЦА
@app.on_message(filters.command("subscribe"))
async def subscribe(client, message: Message):
    user_id = message.from_user.id
    config_data = read_config() 
    if user_id not in config_data.get('subscribed_users', []):
        config_data.setdefault('subscribed_users', []).append(user_id)
        write_config(config_data)
        await message.reply("You are now subscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    else:
        await message.reply("You are already subscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ОТПИСАТЬСЯ
@app.on_message(filters.command("unsubscribe"))
async def unsubscribe(client, message: Message):
    user_id = message.from_user.id
    config_data = read_config()
    if user_id in config_data.get('subscribed_users', []):
        config_data['subscribed_users'].remove(user_id)
        write_config(config_data)
        await message.reply("You are now unsubscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    else:
        await message.reply("You are not subscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ДОБАВИТЬ KEYWORD
@app.on_message(filters.command("add_keyword"))
async def add_keyword(client, message: Message):
    user_id = message.from_user.id
    await add_user_status(2, user_id)
    await message.reply("Please send me the keyword/keywords \n Format: keyword1;keyword2")

# УДАЛИТЬ KEYWORD
@app.on_message(filters.command("remove_keyword"))
async def remove_keyword(client, message: Message):
    user_id = message.from_user.id
    await add_user_status(-2, user_id)
    await message.reply("Write keyword")

# СПИСОК KEYWORDS И КАНАЛОВ
@app.on_message(filters.command("list"))
async def list_channels_keywords(client, message: Message):
    chat_id = message.chat.id
    channels_str = await read_channels_info(chat_id)
    keywords_str = await read_keywords_info(chat_id)
    response = f"Monitored Channels: {channels_str}\nKeywords: {keywords_str}"
    await message.reply(response, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Функция для проверки, содержит ли сообщение любое ключевое слово
def contains_keyword(text):
    words = re.findall(r'\w+', text.lower())
    normalized_words = {normalize_word(word, 'english') for word in words}
    normalized_words.update(normalize_word(word, 'russian') for word in words)

    normalized_keywords = {normalize_word(keyword, 'english') for keyword in KEYWORDS}
    normalized_keywords.update(normalize_word(keyword, 'russian') for keyword in KEYWORDS)

    return any(keyword in normalized_words for keyword in normalized_keywords)

########################################################################################
########################################################################################
# ОПЛАТА
########################################################################################
########################################################################################
"""@app.on_message(filters.text & filters.channel)
async def handle_channel_messages(client, message: Message):
    if message.chat.username in CHANNELS and contains_keyword(message.text):
        for user_id in SUBSCRIBED_USERS:
            await app.forward_messages(user_id, message.chat.id, message.message_id)
            await app.send_message(user_id, "New message with keyword received.")"""
# Основной обработчик сообщений

@app.on_message(filters.private & ~filters.command("add_channel"))
async def handle_message(client, message: Message):
    user_id = message.from_user.id
    state = await read_status_info(user_id)
    print(state)
    if state == 1:
        # Сохраняем сообщение в базу данных
        channel = message.text
        chat_id = message.chat.id
        channels_atm = await read_channels_info(chat_id)
        channels_atm = channels_atm.split(";")
        if channel.count("@") - 1 == channel.count(";") and ("@@" or "@;" or ";;") not in channel and channel[-1] != ";" and channel not in channels_atm:
            channels_atm = ";".join(channels_atm)
            channels_to_db = channels_atm + ";" + channel
            if channels_to_db[0] == ";":
                channels_to_db = channels_to_db[1:]
            await add_channel_to_db(channels_to_db, chat_id)
            await message.reply(f"Channel '{channel}' saved.")
        else:
            await message.reply("Write the channel names in the correct format")
        await add_user_status(0, user_id)
    if state == 2:
        # Сохраняем сообщение в базу данных
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        keywords_atm = keywords_atm.split(";")
        if keyword != "." and keyword[-1] != ";" and keyword not in keywords_atm:
            keywords_atm = ";".join(keywords_atm)
            keywords_to_db = keywords_atm + ";" + keyword
            if keywords_to_db[0] == ";":
                keywords_to_db = keywords_to_db[1:]
            await add_keyword_to_db(keywords_to_db, chat_id)
            await message.reply(f" '{keyword}' saved.")
        else:
            await message.reply("Write the keyword names in the correct format")
        await add_user_status(0, user_id)
    if state == -1:
        channel = message.text
        chat_id = message.chat.id
        channel_atm = await read_channels_info(chat_id)
        channel_atm = channel_atm.split(";")
        if channel in channel_atm:
            channel_atm.remove(channel)
            channel_atm = ";".join(channel_atm)
            await add_channel_to_db(channel_atm, chat_id)
            await message.reply(f" '{channel}' deleted.")
        else:
            await message.reply("Write the channel name in the correct format")
        await add_user_status(0, user_id)
    if state == -2:
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        keywords_atm = keywords_atm.split(";")
        if keyword in keywords_atm:
            keywords_atm.remove(keyword)
            keywords_atm = ";".join(keywords_atm)
            await add_keyword_to_db(keywords_atm, chat_id)
            await message.reply(f" '{keyword}' deleted.")
        else:
            await message.reply("Write the keyword name in the correct format")
        await add_user_status(0, user_id)
if __name__ == "__main__":
    app.run()


"""@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    chat_id = message.chat.id
    result = await read_info(chat_id)
    if result == 1:
       await bot.send_message(message.chat.id, "Подписка уже есть") 
    else:
        if PAYMENT_TOKEN.split(':')[1] == "TEST":
            await bot.send_message(message.chat.id, "Тестовый платеж")
        await bot.send_invoice(message.chat.id,
                            title="Подписка на парсер",
                            description="Активация подписки на 1 месяц",
                            provider_token="381764678:TEST:71533",
                            currency="RUB",
                            is_flexible="False",
                            prices=[PRICE],
                            start_parameter="one-month-subscription",
                            payload="test-invoice-payload")"""