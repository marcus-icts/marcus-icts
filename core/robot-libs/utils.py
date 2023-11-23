import base64

from core.env import env
from dataUriCaptcha import dataUriCaptcha
from robot.api.logger import console
from robot.running import EXECUTION_CONTEXTS


def write_results(data):
    xml_logger = EXECUTION_CONTEXTS.current.output._xmllogger
    xml_logger._writer.element('crawler-result', data)


def convert_currency(page, amount, from_currency, to_currency):
    """
    Converte uma moeda para outra
    :param page: Página atual do navegador
    :param amount: Valor a ser convertido
    :param from_currency: Moeda de origem
    :param to_currency: Moeda de destino
    :return:
    """

    try:
        url = 'https://www.xe.com/currencyconverter/convert/'

        page.goto(
            url=f"{url}?Amount={amount}&From={from_currency}&To={to_currency}",
            timeout=120000
        )

        money_result = page.wait_for_selector(
            'main > div > div:nth-child(2) > div:nth-child(1) > p[class^=result__BigRate]'
        )

        if not money_result:
            raise Exception("Não foi possível converter a moeda.")

        money_text = float(money_result.inner_text().strip().split(" ")[0].replace(",", ""))
        money_transformed = "{:.2f}".format(money_text)

    except Exception as e:
        console(f"Erro: {e}")
        money_transformed = amount

    console(f"Valor convertido: {amount} -> {money_transformed}")
    return money_transformed

def solve_captcha_from_image(image):
    """
    Resolve o captcha da imagem
    :param image: Imagem do captcha
    :return: String
    """
    solver = dataUriCaptcha()
    solver.set_key(env('CAPTCHA_KEY'))
    captcha_text = solver.solve_and_return_solution(base64.encodebytes(image))
    return captcha_text
