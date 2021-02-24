import json
from types import SimpleNamespace
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from .logger import get_logger
from .env import env
from .exceptions import InvalidMessageException, InvalidMessagePayloadException

def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
  '''
  Callback executado em cada mensagem recebida na fila de entrada.
  '''

  if properties.reply_to is None or properties.correlation_id is None:
    raise InvalidMessagePayloadException("Missing 'reply_to' or 'correlation_id'")

  try:
    request = json.loads(body.decode('UTF-8'), object_hook=lambda x: SimpleNamespace(**x))
  except json.JSONDecodeError:
    raise InvalidMessageException("Not a valid JSON")

  if not hasattr(request, 'subject') or not hasattr(request, 'related_data'):
    raise InvalidMessageException("Missing 'subject' or 'related_data'")

  ch.basic_ack(method.delivery_tag)

def callback_wrapper(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
  '''
  Um wrapper para o callback da fila de entrada, dessa forma qualquer erro
  não previsto será jogado para uma fila de erro, sem quebrar o consumidor
  '''

  logger = get_logger()
  logger.info(" [x] Received %r" % body)
  try:
    on_message_callback(ch, method, properties, body)
  except Exception as e:
    ch.basic_publish(
      '',
      '{0}.error'.format(env('RABBIT_QUEUE_PREFIX', 'project-zeta')),
      json.dumps({
        'properties': properties.__dict__,
        'body': '%r' % body,
        'err_repr': repr(e),
        'err_str': str(e)
      }, ensure_ascii=False)
    )
    ch.basic_ack(method.delivery_tag)
    logger.error(" [x] Unexpected error while processing message: %s. Message: '%r'. The message was forwarded to the error queue." % (repr(e), body))
