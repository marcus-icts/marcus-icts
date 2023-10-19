import sys
import os
import pika
from .logger import setup_logger, get_logger
import json
import signal
from typing import Callable
from robot.api.deco import library
from .env import env, init_env

import robot.api.logger as logger

class RabbitMQ:
    def __init__(self):
        init_env()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                env('RABBITMQ_HOST', '127.0.0.1'),
                heartbeat=6000,
                credentials=pika.credentials.PlainCredentials(
                    env('RABBITMQ_USER', 'guest'),
                    env('RABBITMQ_PASS', 'guest')
                )
            )
        )
        self.channel = self.connection.channel()
        self.logger = logger
        # self.defautArgs = dict{"x-max-priority": 10}

    def verifyqueue(self, queue:str):
        self.channel.queue_declare(
            queue=queue,
            durable=True
        )
        # self.channel.queue_declare(queue, False,True,False,False,self.defautArgs)

    def push(self, queue: str, data: bytes, reply_to: str = None, priority: int = 7):
        self.verifyqueue(queue=queue)
        body = json.dumps(
            data,
            indent=4,
            sort_keys=True,
            ensure_ascii=False
        )
        properties = pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            reply_to=reply_to,
            priority=priority
        )
        self.channel.basic_publish(
            '',
            routing_key=queue,
            properties=properties,
            body=body
        )

    def listen(self, queue:str, callback:Callable, consumer:str = ''):
        self.verifyqueue(queue=queue)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue,
            consumer_tag=consumer,
            on_message_callback=callback
        )
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        self.logger.console("********* Waiting for messages.  To exit press ctrl + C *********\n\n");
        try:
            self.channel.start_consuming()
        except Exception as e:
            self.logger.console(str(e))
            raise e
        finally:
            # Garantir que a conexão seja fechada corretamente
            self.channel.stop_consuming()
            self.channel.close()
            self.connection.close()
            try:
                sys.exit(1)
            except SystemExit:
                os._exit(1)

    def handle_interrupt(self, signum, frame):
        self.logger.console(f"Recebido sinal {signum} do {frame}.\n [!] Encerrando o consumidor.\n\n")
        raise Exception(f"Sinal {signum} recebido.")
