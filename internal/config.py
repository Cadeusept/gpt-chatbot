import os

from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
INPUT_QUEUE = os.getenv('INPUT_QUEUE', 'input_queue')
OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', 'output_exchange')
RESULT_ROUTING_KEY = os.getenv('RESULT_ROUTING_KEY', 'result')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
DEEPSEEK_EMAIL = os.getenv('DEEPSEEK_EMAIL')
DEEPSEEK_PASSWORD = os.getenv('DEEPSEEK_PASSWORD')
