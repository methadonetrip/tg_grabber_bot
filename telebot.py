from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
from db import add_user_to_db, add_payment_to_db, read_info
from db import connection
import pymysql

PAYMENT_TOKEN = "" # нужно указать токен
bot = Bot('') # нужно указать api бота
PRICE = types.LabeledPrice(label="Подписка на парсер", amount=15000)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    await add_user_to_db(chat_id)
    await bot.send_message(message.chat.id, "Привествуем в боте ... ")

@dp.message_handler(commands=['buy'])
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
                            payload="test-invoice-payload")
    


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok = True)
    


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")
    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount / 100} {message.successful_payment.currency} прошел успешно")
    chat_id = message.chat.id
    await add_payment_to_db(chat_id)
    await bot.send_message(message.chat.id,
                           "Ваша подписка активна, желаем приятного пользования!")
    
executor.start_polling(dp, skip_updates = False)
