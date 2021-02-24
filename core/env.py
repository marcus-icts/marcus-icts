from dotenv import load_dotenv
from os import getenv

def env(key: str, default: str = None):
  '''
  Função utilizada para se obter o valor de uma variável de ambiente ou um valor padrão
  '''
  found = getenv(key)
  return default if found == None else found

def init_env(): load_dotenv()
