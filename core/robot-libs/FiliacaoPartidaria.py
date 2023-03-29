from core.env import env
from utils import write_results
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import json
import requests
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class FiliacaoPartidaria(NewCoreLib.NewCoreLib):
    @keyword('Filiacao Partidaria - TSE')
    def get_tse_token(self, url_api_generate: str, website_key: str, name: str, voters_card: str, birth_date: str, mothers_name: str = '', fathers_name: str = ''):
        try:
            data = {}
            positive_message = 'ESTÁ REGULARMENTE FILIADO .'
            negative_message = 'NÃO ESTÁ FILIADO A PARTIDO POLÍTICO .'

            solver = recaptchaV2Proxyless()
            solver.set_verbose(1)
            solver.set_key(env('CAPTCHA_KEY'))
            solver.set_website_url(url_api_generate)
            solver.set_website_key(website_key)
            g_response = solver.solve_and_return_solution()

            headers = {
                "Accept": "application/json; charset=utf-8",
                "Content-Type": "application/json; charset=utf-8"
            }

            body = {
                "tipoCertidao": 2,
                "nomeEleitor": name,
                "nomePai": fathers_name,
                "nomeMae": mothers_name,
                "recaptcha": g_response,
                "dataNascimento": birth_date,
                "numeroTituloEleitor": voters_card,
            }

            response = requests.post(
                url_api_generate, json=body, headers=headers)

            try:
                content = json.loads(response.content)

                situation = content['situacao']
                data_occurrence = content['dadosOcorrencia']

                if (situation == positive_message):
                    data['alertas'] = 1
                    data['found'] = True
                    data['situacao'] = situation
                    data['dadosOcorrencia'] = data_occurrence
                elif (situation == negative_message):
                    data['alertas'] = 0
                    data['found'] = True
                    data['situacao'] = situation
                else:
                    raise Exception('resultado fora do esperado')
            except json.decoder.JSONDecodeError:
                data['found'] = False

            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)
