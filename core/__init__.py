import sys, os, json
from pika import BlockingConnection, ConnectionParameters
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPConnectionError

from .logger import setup_logger, get_logger
from .env import env, init_env
from .consumer import callback_wrapper

def _consume():
  '''
  Se conecta ao RabbitMQ, configura as filas utilizadas e começa a consumir da fila de input
  '''

  queue_prefix = env('RABBIT_QUEUE_PREFIX', 'icts-crawler')
  conn = BlockingConnection(ConnectionParameters(
    env('RABBITMQ_HOST', '127.0.0.1'),
    credentials=PlainCredentials(
      env('RABBITMQ_USER', 'guest'),
      env('RABBITMQ_PASS', 'guest')
    )
  ))
  channel = conn.channel()
  channel.queue_declare('{0}.error'.format(queue_prefix), False, True, False, False)
  channel.queue_declare('{0}.input'.format(queue_prefix), False, True, False, False)
  channel.basic_consume('{0}.input'.format(queue_prefix), callback_wrapper)
  get_logger().info(' [*] Waiting for messages. To exit press CTRL+C')
  channel.start_consuming()

def _exit(code):
  try:
    sys.exit(code)
  except SystemExit:
    os._exit(code)
    raise

def main():
  init_env()

  setup_logger()
  logger = get_logger()

  try:
    _consume()
  except KeyboardInterrupt:
    _exit(0)
  except AMQPConnectionError:
    logger.error("Não foi possível se conectar ao servidor do RabbitMQ (host: {0})".format(env('RABBITMQ_HOST', '127.0.0.1')))
    _exit(1)
  except Exception as e:
    logger.error("Erro não esperado: {0}. {1}.".format(sys.exc_info()[0], repr(e)))
    _exit(1)

