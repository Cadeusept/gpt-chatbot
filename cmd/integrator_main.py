import json
from dotenv import load_dotenv
import os

import internal.handlers.mq.rmq as rmq
import internal.clients.openai.client as oai

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

def process_message(ch, method, properties, body):
    message = json.loads(body)
    image_base64 = message.get("image", "")
    text = message.get("text", "")

    client = oai.Client(OPENAI_API_KEY)
    result = client.analyze_content(text, image_base64)
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