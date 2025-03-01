import json
import base64

import internal.handlers.mq
import pika
import uuid
import openai
from dotenv import load_dotenv
import os

import internal.handlers.mq as mq

# Загрузка переменных окружения
load_dotenv()

# Конфигурация RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
INPUT_QUEUE = os.getenv('INPUT_QUEUE', 'input_queue')
OUTPUT_QUEUE = os.getenv('OUTPUT_QUEUE', 'output_queue')
OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', 'output_exchange')

# Конфигурация OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=INPUT_QUEUE)
    channel.basic_consume(queue=INPUT_QUEUE, on_message_callback=mq.process_message, auto_ack=False)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()