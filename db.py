import pymysql
import pymysql.cursors
from config import host, user, password, db_name

connection = pymysql.connect(host=host,
                        port=3306,
                        user=user,
                        password=password,
                        database=db_name,
                        cursorclass=pymysql.cursors.DictCursor)

async def add_user_to_db(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO usersid (id) VALUES (%s) ON DUPLICATE KEY UPDATE id = id"
            cursor.execute(sql, (chat_id,))
        connection.commit() # connection is not autocommit by default.
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_payment_to_db(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE usersid SET sub = '%s' WHERE id = %s"
            cursor.execute(sql, (1, chat_id))
        connection.commit() # connection is not autocommit by default.
    except Exception as e:
        print(f"Error adding user to database: {e}")
 

async def read_info(id):
    try:
        with connection.cursor() as cursor:
            # Выполняем SQL-запрос для получения значения 'sum' по 'id'
            sql = f"SELECT `sub` FROM usersinfo.usersid WHERE `id` = {id}"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                sub_values = [value for key, value in result.items() if key == 'sub']
                return sub_values[0]
            else:
                return 0

    except Exception as e:
        return f"Произошла ошибка: {e}"
