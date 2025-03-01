import json

import internal.clients.openai.client as openai_client

class MQ:
    def __init__(self, host: str):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

    def publish(self, queue: str, message: dict):
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message))

    def consume(self, queue: str, callback):
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
        print(f"[*] Waiting for messages in {queue}. To exit press CTRL+C")
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
