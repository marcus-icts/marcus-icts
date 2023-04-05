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
class CertidaoEmbargos(NewCoreLib.NewCoreLib):
    @keyword('Certidao Embargos - PF')
    def certificate_embargo_pf(self, cpf: str):
        try:
            data = {}
            cpf_formatted = re.sub('[^0-9]', '', cpf)
            pdf_file_name = 'certidao_embargos_pf_' + cpf_formatted + '.pdf'
            url = 'https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php?modulo=publico/areasembargadas/CertidaoNadaConsta.php&$bvars=' + \
                str(cpf_formatted) + '&ajax=1&fpdf=1'

            try:
                # O verify foi setado para False porque o site está com problemas no certificado SSL
                response = requests.get(url, verify=False)

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

            except requests.exceptions.RequestException as e:
                data['found'] = False

            console('Remover o pdf...')
            os.remove(pdf_file_name)
            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)

    @keyword('Certidao Embargos - PJ')
    def certificate_embargo_pj(self, cnpj: str):
        try:
            data = {}
            cnpj_formatted = re.sub('[^0-9]', '', cnpj)
            pdf_file_name = 'certidao_embargos_pf_' + cnpj_formatted + '.pdf'
            url = 'https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php?modulo=publico/areasembargadas/CertidaoNadaConsta.php&$bvars=' + \
                str(cnpj_formatted) + '&ajax=1&fpdf=1'

            try:
                # O verify foi setado para False porque o site está com problemas no certificado SSL
                response = requests.get(url, verify=False)

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

            except requests.exceptions.RequestException as e:
                data['found'] = False

            console('Remover o pdf...')
            os.remove(pdf_file_name)
            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)
