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

from db import add_user_to_db, add_payment_to_db, read_info
from yookassa_integration import YooKassaIntegration
from config import host, user, password, db_name, bot_token
lemmatizer = WordNetLemmatizer()
morph = MorphAnalyzer()

# Загрузка названий каналов и ключевых слов из файла JSON
with open('channels.json', 'r') as file:
    data = json.load(file)
CHANNELS = data.get('channels', [])
KEYWORDS = data.get('keywords', [])
SUBSCRIBED_USERS = set()
api_id = 'ВАШ_API_ID'     # Замените на ваш Telegram API ID
api_hash = 'ВАШ_API_HASH' # Замените на ваш Telegram API Hash
bot_token = '6776409787:AAEOHAIOpKMdTK9dFhQVJRLB09c3lqd5-HQ'
app = Client("grabber_bot", api_id=api_id, api_hash=api_hash)

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
    [KeyboardButton('subscribe'), KeyboardButton('unsubscribe'), KeyboardButton('list')],
    [KeyboardButton('add_channel'), KeyboardButton('add_keyword')],
    [KeyboardButton('remove_channel'), KeyboardButton('remove_keyword')]
]
# Команда для запуска бота
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("Bot is running. Use the keyboard below:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ДОБАВЛЕНИЕ КАНАЛА
@app.on_message(filters.command("add_channel"))
async def add_channel(client, message: Message):
    try:
        channel = message.text.split(' ', 1)[1]
        config_data = read_config()
        if channel not in config_data['channels']:
            config_data['channels'].append(channel)
            write_config(config_data)
            await message.reply(f"Channel {channel} added successfully.")
        else:
            await message.reply(f"Channel {channel} is already in the list.")
    except IndexError:
        await message.reply("Please provide a channel name after the command.")

# УБРАТЬ КАНАЛ
@app.on_message(filters.command("remove_channel"))
async def remove_channel(client, message: Message):
    try:
        channel = message.text.split(' ', 1)[1]
        config_data = read_config()
        if channel in config_data['channels']:
            config_data['channels'].remove(channel)
            write_config(config_data)
            await message.reply(f"Channel {channel} removed successfully.")
        else:
            await message.reply(f"Channel {channel} not found in the list.")
    except IndexError:
        await message.reply("Please provide a channel name after the command.")

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
    try:
        keyword = message.text.split(' ', 1)[1]
        config_data = read_config()
        if keyword not in config_data['keywords']:
            config_data['keywords'].append(keyword)
            write_config(config_data)
            await message.reply(f"Keyword '{keyword}' added successfully.")
        else:
            await message.reply(f"Keyword '{keyword}' is already in the list.")
    except IndexError:
        await message.reply("Please provide a keyword after the command.")

# УДАЛИТЬ KEYWORD
@app.on_message(filters.command("remove_keyword"))
async def remove_keyword(client, message: Message):
    try:
        keyword = message.text.split(' ', 1)[1]
        config_data = read_config()
        if keyword in config_data['keywords']:
            config_data['keywords'].remove(keyword)
            write_config(config_data)
            await message.reply(f"Keyword '{keyword}' removed successfully.")
        else:
            await message.reply(f"Keyword '{keyword}' not found in the list.")
    except IndexError:
        await message.reply("Please provide a keyword after the command.")

# СПИСОК KEYWORDS И КАНАЛОВ
@app.on_message(filters.command("list"))
async def list_channels_keywords(client, message: Message):
    channels_str = ', '.join(CHANNELS)
    keywords_str = ', '.join(KEYWORDS)
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
@app.on_message(filters.command("add_user"))
async def handle_add_user(client, message: Message):
    chat_id = message.chat.id
    await add_user_to_db(chat_id)
    await message.reply("User added to the database.")

@app.on_message(filters.command("add_payment"))
async def handle_add_payment(client, message: Message):
    chat_id = message.chat.id
    await add_payment_to_db(chat_id)
    await message.reply("Payment information updated in the database.")

@app.on_message(filters.command("check_sub"))
async def handle_check_sub(client, message: Message):
    chat_id = message.chat.id
    sub_status = await read_info(chat_id)
    if sub_status is not None:
        await message.reply(f"Subscription status: {sub_status}")
    else:
        await message.reply("Unable to check subscription status.")

# Initialize YooKassa Integration
yoo_kassa = YooKassaIntegration(shop_id="your_shop_id", secret_key="your_secret_key")
# Initialize Pyrogram Client
app = Client("my_bot", api_id="your_api_id", api_hash="your_api_hash", bot_token="your_bot_token")
# Constants
PRICE = 15000  # Amount in smallest currency unit, e.g., cents for USD

@app.on_message(filters.command("buy"))
async def buy(client, message: Message):
    chat_id = message.chat.id
    result = await read_info(chat_id)
    if result == 1:
        await client.send_message(chat_id, "Subscription already exists")
    else:
        payment_link, payment_id = yoo_kassa.create_payment(amount=PRICE / 100)  # Convert to main currency unit
        if payment_link:
            await client.send_message(chat_id, "Please pay here: " + payment_link)
            # Here you might want to store the payment_id with the user's info
        else:
            await client.send_message(chat_id, "Error creating payment link")

# You can create a function to check payment status periodically or rely on webhook
async def check_payment_status(client, chat_id, payment_id):
    status = yoo_kassa.check_payment_status(payment_id)
    if status == "succeeded":
        await client.send_message(chat_id, "Payment successful. Subscription activated!")
        # Update the database with subscription status
    elif status == "pending":
        # Recheck after some time
        await asyncio.sleep(60)  # Wait for 60 seconds before rechecking
        await check_payment_status(client, chat_id, payment_id)
    else:
        await client.send_message(chat_id, "Payment failed or cancelled")

async def find_chat_id_by_payment_id(payment_id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT chat_id FROM payments WHERE payment_id = %s", (payment_id,))
            result = cursor.fetchone()
            return result['chat_id'] if result else None
        except Exception as e:
            print(f"Error finding chat ID by payment ID: {e}")
            return None
# Additional function to handle webhook notification (this is just a placeholder)
async def webhook_handler(data):
    payment_id, status = yoo_kassa.handle_webhook(data)
    if status == "succeeded":
        # Find user associated with this payment_id and notify them
        chat_id = find_chat_id_by_payment_id(payment_id)
        await app.send_message(chat_id, "Payment successful. Subscription activated!")
        # Update the database with subscription status

# Основной обработчик сообщений
@app.on_message(filters.text & filters.channel)
async def handle_channel_messages(client, message: Message):
    if message.chat.username in CHANNELS and contains_keyword(message.text):
        for user_id in SUBSCRIBED_USERS:
            await app.forward_messages(user_id, message.chat.id, message.message_id)
            await app.send_message(user_id, "New message with keyword received.")

# Запуск клиента
if __name__ == '__main__':
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