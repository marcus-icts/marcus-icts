import logging
from env import env

def get_logger():
  return logging.getLogger('zeta-logger')

def setup_logger():
  logger = logging.getLogger('zeta-logger')
  logger.setLevel(logging.INFO)

  fh = logging.FileHandler('logs/zeta.log')
  fh.setLevel(env('LOGGER_LEVEL', 'ERROR'))
  fh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

  logger.addHandler(fh)
  logger.addHandler(ch)
