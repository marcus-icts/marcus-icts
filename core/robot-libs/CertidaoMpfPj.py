from core.env import env
from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import os
import re
import json
import base64
import requests
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class CertidaoMpfPj(NewCoreLib.NewCoreLib):
    @keyword('Certidao MPF - PJ')
    def certificate_mpf_pj(self, cnpj: str):
        try:
            data = {}
            cnpj_formatted = re.sub('[^0-9]', '', cnpj)
            website_key = '6LeUowITAAAAAOIiAB441SS3EF77AS4ZuK0LFsaH'
            pdf_file_name = 'certidao_mpf_pj_' + cnpj_formatted + '.pdf'
            url = 'https://aplicativos.mpf.mp.br/ouvidoria/app/cidadao/certidao'
            api_url = 'https://aplicativos.mpf.mp.br/ouvidoria/rest/v1/publico/certidao'

            console('Resolvendo recaptcha...')
            solver = recaptchaV2Proxyless()
            solver.set_verbose(1)
            solver.set_key(env('CAPTCHA_KEY'))
            solver.set_website_url(url)
            solver.set_website_key(website_key)
            g_response = solver.solve_and_return_solution()
            console('Recaptcha resolvido')

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            url_params = '/emitir?documento=' + \
                str(cnpj_formatted) + '&recaptcha=' + \
                str(g_response) + '&tipoPessoa=J'

            full_request = str(api_url) + str(url_params)

            try:
                response = requests.get(full_request, headers=headers)
                console('Requisição para pegar o data id...')
                console(response.status_code)
                content = json.loads(response.content)

                if (response.status_code == 200):
                    dataId = content['data']

                    url_to_download_pdf = str(api_url) + '/download/' + str(dataId)

                    response = requests.get(url_to_download_pdf)
                    console('Baixando pdf...')
                    if (response.status_code != 200):
                        raise Exception(response.content)

                    with open(pdf_file_name, 'wb') as pdf_file:
                        pdf_file.write(response.content)
                        console('Criando um novo pdf...')

                    with open(pdf_file_name, 'rb') as file:
                        pdf_bytes = file.read()
                        console('Lendo o arquivo PDF como bytes...')

                    console('Codificar o arquivo PDF como Base64...')
                    pdf_base64_bytes = base64.b64encode(pdf_bytes)
                    evidence_b64 = pdf_base64_bytes.decode('utf-8')

                    data['evidence'] = 'data:application/pdf;base64,{}'.format(
                        evidence_b64)
                    data['found'] = True
                    data['evidence_type'] = 'pdf'
                    console('Remover o pdf...')
                    os.remove(pdf_file_name)
                elif (response.status_code == 400 and (content['error']['message'] == 'CPF/CNPJ inexistente/inválido')):
                    data['evidence'] = 'Pessoa jurídica não localizada com o CNPJ informado'
                    data['found'] = True
                    data['evidence_type'] = 'text'
                else :
                    raise Exception(response) 

            except requests.exceptions.RequestException as e:
                data['found'] = False
                raise e
            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)
