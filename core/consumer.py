import json, os
from types import SimpleNamespace
from time import time

from robot.run import run
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from xml.etree.ElementTree import parse as parse_xml

from .logger import get_logger
from .env import env
from .exceptions import InvalidMessageException, InvalidMessagePayloadException, TaskFailedException

def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
  '''
  Callback executado em cada mensagem recebida na fila de entrada.
  '''

  logger = get_logger()
  cwd = os.getcwd()

  # Validações da mensagem e das propriedades
  if properties.reply_to is None or properties.correlation_id is None:
    raise InvalidMessagePayloadException("Missing 'reply_to' or 'correlation_id'")

  try:
    request = json.loads(body.decode('UTF-8'))
  except json.JSONDecodeError:
    raise InvalidMessageException("Not a valid JSON")

  if not 'subject' in request or not 'related_data' in request:
    raise InvalidMessageException("Missing 'subject' or 'related_data'")

  # Parsea o JSON de related_data para as variáveis da execução das tarefas
  variables = list(map(lambda kv: '{0}:{1}'.format(kv, request['related_data'][kv]), request['related_data']))

  # Gera o nome do arquivo de output
  output_file = '{}/robot/results/{}-{}.xml'.format(cwd, time(), properties.correlation_id)

  # Executa a task do Robot
  logger.info('\tRobot task started...')
  run('{}/crawlers/{}.robot'.format(cwd, request['subject']), output=output_file, log=None, report=None, console='quiet', variable=variables)
  logger.info('\t... robot task finished')

  # Faz o parse do arquivo de saída
  request['result'] = json.loads(parse_result(output_file))
  os.remove(output_file)

  ch.basic_ack(method.delivery_tag)

  # Envia a resposta para fila de resposta
  ch.queue_declare(properties.reply_to)
  ch.basic_publish('', properties.reply_to, json.dumps(request, ensure_ascii=False), BasicProperties(correlation_id=properties.correlation_id))


def parse_result(file):
  '''
  Função utilizada para fazer o "parse" do arquivo output.xml gerado pelo
  Robot em busca do resultado da busca e também verificar se houve erros ao executar a task
  '''

  tree = parse_xml(file)
  status = tree.find('./suite/test[1]/status')
  if status.attrib['status'] == 'FAIL':
    raise TaskFailedException(status.text)

  result = tree.find('./suite/test/kw/crawler-result')
  return result.text

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
