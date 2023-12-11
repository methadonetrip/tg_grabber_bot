import pymysql
import pymysql.cursors
from pyrogram import Client, filters
from pyrogram.types import Message
from config import host, user, password, db_name, bot_token

# Настройка подключения к базе данных
connection = pymysql.connect(host=host,
                             port=3306,
                             user=user,
                             password=password,
                             database=db_name,
                             cursorclass=pymysql.cursors.DictCursor)

app = Client("my_bot", bot_token=bot_token)

# Функции для работы с базой данных

async def add_user_to_db(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO usersid (id) VALUES (%s) ON DUPLICATE KEY UPDATE id = id"
            cursor.execute(sql, (chat_id,))
        connection.commit()
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_payment_to_db(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE usersid SET sub = '%s' WHERE id = %s"
            cursor.execute(sql, (1, chat_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating payment info in database: {e}")

async def read_info(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `sub` FROM usersinfo.usersid WHERE `id` = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                return result.get('sub', 0)
            else:
                return 0
    except Exception as e:
        print(f"Error reading user info from database: {e}")
        return None

# Обработчики сообщений

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

# Дополнительные функции и обработчики

# Функция для логирования сообщений
async def log_message(message: Message):
    print(f"User {message.from_user.id} sent a message: {message.text}")

# Обработчик всех текстовых сообщений для логирования
@app.on_message(filters.text)
async def handle_text_messages(client, message: Message):
    await log_message(message)

# Функция для отображения помощи
async def show_help(message: Message):
    help_text = """
    /add_user - Add a user to the database
    /add_payment - Update payment information
    /check_sub - Check subscription status
    """
    await message.reply(help_text)

# Обработчик команды помощи
@app.on_message(filters.command("help"))
async def handle_help(client, message: Message):
    await show_help(message)

# Запуск бота
if __name__ == "__main__":
    app.run()
