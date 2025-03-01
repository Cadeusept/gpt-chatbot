import json

import pika

class MQ:
    def __init__(self, host: str, username: str, password: str):
        self.credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=self.credentials))
        self.channel = self.connection.channel()

    def publish(self, exchange: str, routing_key: str, message: dict):
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message).encode('utf-8'))

    def consume(self, queue: str, callback):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
        print(f"[*] Waiting for messages in {queue}. To exit press CTRL+C")
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
