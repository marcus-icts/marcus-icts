import logging
from .env import env

def get_logger():
  return logging.getLogger('icts-crawler')

def setup_logger():
  logger = logging.getLogger('icts-crawler')
  logger.setLevel(logging.INFO)

  fh = logging.FileHandler('{0}/logs/crawler.log'.format(env('APP_PATH')))
  fh.setLevel(env('LOGGER_LEVEL', 'ERROR'))
  fh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

  logger.addHandler(fh)
  logger.addHandler(ch)
