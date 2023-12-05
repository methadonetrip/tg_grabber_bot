import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# Load channel names and keywords from a JSON file
with open('channels.json', 'r') as file:
    data = json.load(file)

CHANNELS = data.get('channels', [])
KEYWORDS = data.get('keywords', [])

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Command to start the bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Bot is running. Use /subscribe to receive messages.")

# Command to subscribe to keyword notifications
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    # Store user chat_id to send future notifications
    # You can use a database for persistent storage
    user_id = message.from_user.id
    # TODO: Add user_id to a database for persistent storage

    await message.reply("You are subscribed. You will receive messages with keywords.")

# Function to check if a message contains any keyword
def contains_keyword(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

# Main message handler
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_messages(message: types.Message):
    chat_id = message.chat.id
    text = message.text

    # Check if the message contains any keyword
    if contains_keyword(text):
        # Forward the message to all subscribed users
        # TODO: Retrieve user_ids from the database and forward the message
        for user_id in SUBSCRIBED_USERS:
            await bot.forward_message(user_id, chat_id, message.message_id)
            await bot.send_message(user_id, "New message with keyword received!")

if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp, skip_updates=True)
