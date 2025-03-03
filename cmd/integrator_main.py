import json
from dotenv import load_dotenv
import os
import base64

import internal.handlers.mq.rmq as rmq
import internal.clients.openai.client as oai
import internal.clients.deepseek.client as deepseek

# Загрузка переменных окружения
load_dotenv()

# Конфигурация RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
INPUT_QUEUE = os.getenv('INPUT_QUEUE', 'input_queue')
OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', 'output_exchange')
RESULT_ROUTING_KEY = os.getenv('RESULT_ROUTING_KEY', 'ROUTING_KEY')

# Конфигурация OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Конфигурация DeepSeek
DEEPSEEK_EMAIL = os.getenv('DEEPSEEK_EMAIL', '<EMAIL>')
DEEPSEEK_PASSWORD = os.getenv('DEEPSEEK_PASSWORD', '<PASSWORD>')


import base64

def decode_base64(encoded_str: str) -> str:
    """
    Декодирует строку из Base64.

    :param encoded_str: Строка в формате Base64
    :return: Байтовый объект с декодированными данными
    """
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf8')
    except Exception as e:
        raise ValueError(f"Ошибка при декодировании Base64: {e}")

async def process_message(ch, method, properties, body):
    message = json.loads(body)
    image_base64 = message.get("image", "")
    image_url = decode_base64(image_base64)
    text = message.get("text", "")

    openaiClient = oai.Client(OPENAI_API_KEY)
    result = openaiClient.analyze_content(text, image_url)
    result["id"] = message["id"]

    mq = rmq.MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)
    mq.publish(OUTPUT_EXCHANGE, RESULT_ROUTING_KEY, result)
    mq.close()

    deepseekClient = deepseek.Client(DEEPSEEK_EMAIL, DEEPSEEK_PASSWORD)
    result = await deepseekClient.analyze_content(text, image_url)
    result["id"] = message["id"]

    mq = rmq.MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)
    mq.publish(OUTPUT_EXCHANGE, RESULT_ROUTING_KEY, result)
    mq.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    mq = rmq.MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)
    mq.consume(INPUT_QUEUE, process_message)
    mq.close()


if __name__ == "__main__":
    main()