from robot.output.xmllogger import XmlLogger
from robot.running import EXECUTION_CONTEXTS

def write_results(data):
  xml_logger = EXECUTION_CONTEXTS.current.output._xmllogger
  xml_logger._writer.element('crawler-result', data)
