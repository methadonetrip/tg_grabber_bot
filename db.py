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

# Запуск бота
if __name__ == "__main__":
    app.run()
