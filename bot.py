import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Load channel names and keywords from a JSON file
with open('channels.json', 'r') as file:
    data = json.load(file)

CHANNELS = data.get('channels', [])
KEYWORDS = data.get('keywords', [])
SUBSCRIBED_USERS = set()


# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Define custom keyboard
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
subscribe_button = KeyboardButton('subscribe')
unsubscribe_button = KeyboardButton('unsubscribe')
list_button = KeyboardButton('list')
add_channel_button = KeyboardButton('add_channel') # do
add_keyword_button = KeyboardButton('add_keyword') # not 
remove_channel_button = KeyboardButton('remove_channel') # work
remove_keyword_button = KeyboardButton('remove_keyword') # normally
keyboard.row(subscribe_button, unsubscribe_button, list_button)
keyboard.row(add_channel_button, add_keyword_button)
keyboard.row(remove_channel_button, remove_keyword_button)

# Command to start the bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Bot is running. Use the keyboard below:", reply_markup=keyboard)


# Command to subscribe to keyword notifications
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    user_id = message.from_user.id
    SUBSCRIBED_USERS.add(user_id)
    await message.reply("You are subscribed. You will receive messages with your keywords.", reply_markup=keyboard)

# Command to unsubscribe from keyword notifications
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    user_id = message.from_user.id
    SUBSCRIBED_USERS.discard(user_id)
    await message.reply("You are unsubscribed. You will no longer receive messages with your keywords.", \
                        reply_markup=keyboard)

# Command to list currently monitored channels and keywords
@dp.message_handler(commands=['list'])
async def list_channels_keywords(message: types.Message):
    channels_str = ', '.join(CHANNELS)
    keywords_str = ', '.join(KEYWORDS)
    response = f"Monitored Channels: {channels_str}\nKeywords: {keywords_str}"
    await message.reply(response, reply_markup=keyboard)

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
        for user_id in SUBSCRIBED_USERS:
            await bot.forward_message(user_id, chat_id, message.message_id)
            await bot.send_message(user_id, "New message with keyword received.")



# Command to add a channel
@dp.message_handler(commands=['add_channel'])
async def add_channel(message: types.Message):
    try:
        channel = message.text.split(' ', 1)[1]
        CHANNELS.append(channel)
        await message.reply(f"Channel {channel} added successfully.", reply_markup=keyboard)
    except IndexError:
        await message.reply("Please provide a channel name after the command.", reply_markup=keyboard)

# Command to remove a channel
@dp.message_handler(commands=['remove_channel'])
async def remove_channel(message: types.Message):
    try:
        channel = message.text.split(' ', 1)[1]
        CHANNELS.remove(channel)
    except IndexError:
        await message.reply("Please provide a channel name after the command.", reply_markup=keyboard)
    except ValueError:
        await message.reply(f"Channel {channel} not found in the list.", reply_markup=keyboard)
    else:
        await message.reply(f"Channel {channel} removed нахуй successfully.", reply_markup=keyboard) # check if True

# Command to add a keyword
@dp.message_handler(commands=['add_keyword'])
async def add_keyword(message: types.Message):
    try:
        keyword = message.text.split(' ', 1)[1]
        KEYWORDS.append(keyword)
        await message.reply(f"Keyword '{keyword}' added successfully.", reply_markup=keyboard)
    except IndexError:
        await message.reply("Please provide a keyword after the command.", reply_markup=keyboard)

# Command to remove a keyword
@dp.message_handler(commands=['remove_keyword'])
async def remove_keyword(message: types.Message):
    try:
        keyword = message.text.split(' ', 1)[1]
        KEYWORDS.remove(keyword)
        await message.reply(f"Keyword '{keyword}' removed successfully.", reply_markup=keyboard)
    except IndexError:
        await message.reply("Please provide a keyword after the command.", reply_markup=keyboard)
    except ValueError:
        await message.reply(f"Keyword '{keyword}' not found in the list.", reply_markup=keyboard)

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
        for user_id in SUBSCRIBED_USERS:
            await bot.forward_message(user_id, chat_id, message.message_id)
            await bot.send_message(user_id, "New message with keyword received.")

if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp, skip_updates=True)
