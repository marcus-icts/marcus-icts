import os, time, json
from typing import Optional
from xml.etree.ElementTree import parse as parse_xml

from robot.run import run

from .env import env
from .logger import get_logger
from .exceptions import TaskFailedException

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
  return result.text if result is not None else None

def exec_robot(subject: str, related_data: Optional[dict] = None):
  logger = get_logger()

  # Parsea o JSON de related_data para as variáveis da execução das tarefas
  variables = [''] if related_data is None else list(map(lambda kv: '{0}:{1}'.format(kv, related_data[kv]), related_data))

  # Gera o nome do arquivo de output
  output_file = '{}robot/results/{}.xml'.format(env('APP_PATH'), time.time())

  logger.info('\tRobot task started...')
  run('{}crawlers/{}.robot'.format(env('APP_PATH'), subject), output=output_file, log=None, report=None, console='quiet', variable=variables)
  logger.info('\t... robot task finished')
  result = parse_result(output_file)
  result = json.loads(result) if result is not None else None
  os.remove(output_file)
  return result
