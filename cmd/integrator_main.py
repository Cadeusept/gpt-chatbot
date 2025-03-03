import asyncio
import json
import os
import base64

import internal.handlers.mq.rmq as rmq
import internal.clients.openai.client as oai
import internal.clients.deepseek.client as deepseek

from internal.config import *
# Загрузка переменных окружения

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

def process_message(ch, method, properties, body):
    message = json.loads(body)
    image_base64 = message.get("image", "")
    image_url = decode_base64(image_base64)
    text = message.get("text", "")

    # openaiClient = oai.Client(OPENAI_API_KEY)
    # result = openaiClient.analyze_content(text, image_url)
    # result["id"] = message["id"]
    #
    mq = rmq.MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)
    # mq.publish(OUTPUT_EXCHANGE, RESULT_ROUTING_KEY, result)

    deepseekClient = deepseek.Client(DEEPSEEK_EMAIL, DEEPSEEK_PASSWORD)
    result = asyncio.run(deepseekClient.analyze_content(text, image_url))
    result["id"] = message["id"]
    mq.publish(OUTPUT_EXCHANGE, RESULT_ROUTING_KEY, result)

    mq.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    mq = rmq.MQ(RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD)
    mq.consume(INPUT_QUEUE, process_message)
    mq.close()


if __name__ == "__main__":
    main()