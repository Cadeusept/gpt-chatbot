import logging

from pyrogram import Client, filters
from pyrogram.types import Message
import json
from internal.config import *
from internal.handlers.mq.rmq import MQ


class Response:
    model_name: str = None
    verdict: str = None
    reason: str = None
    confidence: str = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH)
mq = MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)

TARGET_CHAT_ID = 1111111

# Функция для отправки сообщений в RabbitMQ
def send_to_rabbitmq(message: dict):
    mq.publish(exchange='', routing_key=INPUT_QUEUE, message=message)
    logger.info(f"Sent to RabbitMQ: {message}")

def process_message(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Функция для получения сообщений из RabbitMQ
def get_from_rabbitmq():
    method_frame, header_frame, body = mq.consume(queue=OUTPUT_EXCHANGE, callback=process_message)
    if method_frame:
        message = json.loads(body)
        logger.info(f"Received from RabbitMQ: {message}")
        return message
    return None


async def fetch_chat_history(chat_id: int):
    async for message in app.get_chat_history(chat_id):
        if message.text:  # Проверяем, что сообщение содержит текст
            message_data = {
                "chat_id": chat_id,
                "message_id": message.id,
                "user_name": message.from_user.first_name if message.from_user else "Unknown",
                "message_text": message.text
            }
            send_to_rabbitmq(message_data)
            logger.info(f"Fetched and sent message: {message.text}")

# Обработчик новых сообщений в беседе
@app.on_message(filters.chat(TARGET_CHAT_ID))
def handle_new_message(client: Client, message: Message):
    chat_title = message.chat.title
    user_name = message.from_user.first_name if message.from_user else "Unknown"
    message_text = message.text

    # Формируем сообщение для отправки в RabbitMQ
    message_data = {
        "chat_title": chat_title,
        "user_name": user_name,
        "message_text": message_text
    }

    # Отправляем сообщение в RabbitMQ
    send_to_rabbitmq(message_data)

async def reply_to_existing_message(chat_id: int, message_id: int, reply_text: str):
    # Получаем сообщение по его ID
    target_message = await app.get_messages(chat_id, message_id)
    # Отвечаем на сообщение
    await target_message.reply(reply_text)
    print(f"Ответ отправлен на сообщение {message_id} в чате {chat_id}")


# Функция для отправки сообщений в беседу Result
async def send_to_result_chat(client: Client):
    while True:
        message = get_from_rabbitmq()
        if message:
            await reply_to_existing_message(TARGET_CHAT_ID, message['id'], message['message_text'])
            # await client.send_message(chat_id=TARGET_CHAT_ID, text=f"{message['user_name']}: {message['message_text']}")

# Запуск бота
if __name__ == "__main__":
    app.start()
    app.run(fetch_chat_history(TARGET_CHAT_ID))
    logger.info("Bot started")

    # Запуск функции для отправки сообщений в беседу Result
    send_to_result_chat(app)

    app.idle()