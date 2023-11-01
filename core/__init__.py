import sys,os,json
from .logger import setup_logger, get_logger
from .env import env, init_env
from .consumer import callback_wrapper
from .robot_runner import exec_robot
from .RabbitMQ import RabbitMQ

def run(subject, related_data):
    init_env()

    setup_logger()

    related_data = None if related_data is None else json.loads(related_data)
    result = exec_robot(subject, related_data)
    get_logger().info(result)

def _exit(code):
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)
