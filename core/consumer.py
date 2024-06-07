import json
import traceback

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from datetime import datetime
from robot.api.logger import console

from .logger import get_logger
from .env import env
from .exceptions import InvalidMessageException, InvalidMessagePayloadException
from .robot_runner import exec_robot


def on_message_callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
    '''
    Callback executado em cada mensagem recebida na fila de entrada.
    '''

    # Validações da mensagem e das propriedades
    if properties.reply_to is None:
        raise InvalidMessagePayloadException("Missing 'reply_to'")

    try:
        request = json.loads(body.decode('UTF-8'))
    except json.JSONDecodeError:
        raise InvalidMessageException("Not a valid JSON")

    if not 'subject' in request or not 'related_data' in request:
        raise InvalidMessageException("Missing 'subject' or 'related_data'")

    request['result'] = exec_robot(request['subject'], request['related_data'])

    ch.basic_ack(method.delivery_tag)

    # Envia a resposta para fila de resposta
    ch.queue_declare(properties.reply_to, durable=True)
    ch.basic_publish('', properties.reply_to, json.dumps(request, indent=4, sort_keys=True, ensure_ascii=False))
    get_logger().info(" [✓] Result published on '{}' queue".format(properties.reply_to))


def callback_wrapper(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
    '''
    Um wrapper para o callback da fila de entrada, dessa forma qualquer erro
    não previsto será jogado para uma fila de erro, sem quebrar o consumidor
    '''

#   logger = get_logger()
#   logger.info(" [x] Received %r" % body)
    console("\n\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"][x] Received %r" % body)
    try:
        on_message_callback(ch, method, properties, body)
    except Exception as e:
        erro = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': str(e),
            'trace': traceback.format_exc()
        }
        request = json.loads(body.decode('UTF-8'))
        request['error'] = erro
        ch.basic_publish(
            '',
            properties.reply_to,
            json.dumps(request, indent=4, sort_keys=True, ensure_ascii=False),
            properties
        )
        ch.basic_ack(method.delivery_tag)
        console("\n["+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"][x] Unexpected error while processing message: %s. \n\nMessage: '%r'. \n\nThe message was repplyed with error\n\n" % (repr(e), request))
        raise InvalidMessagePayloadException("Ocorreu um erro, vamos matar o processo e subir novo consumer para garantir que todos os requisitos sejam restartados.\n\n")
