import time
from core.RabbitMQ import RabbitMQ
from core.consumer import callback_wrapper

RabbitMQ().push(queue='CRAWLER_Test', data='Minha mensagem é essa: hahaha.')

def callback(ch, method, properties, body):
    print(f"Recebido: {body}")
    print(f"properties: {properties}")
    ch.basic_ack(method.delivery_tag)

RabbitMQ().listen(queue='CRAWLER_Test', callback=callback)
