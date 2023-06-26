from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import re
import json, requests
import base64
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class AntecedentesCriminais(NewCoreLib.NewCoreLib):
    @keyword('Antecedentes Criminais')
    def antecedentes(self, cpf: str, name: str, retry: int = 0):
        try:
            console('\nTentativa ' + str(retry + 1) + ' de 5')
            url = 'https://antecedentes.dpf.gov.br/antecedentes-criminais/certidao'
            url_request = 'https://antecedentes.dpf.gov.br/antecedentes-criminais-rest/api/certidoes'
            website_key = '6Lfi3R4bAAAAADTnh5JgSL7xzTSJ2YlFQLek38U1'
            console("Resolvendo recaptcha v2")
            response = self.recaptchaV2(url, website_key)
            tries = 1
            while tries < 4:
                if response == False:
                    console("Problema na resolução do recaptcha. Tentativa número " + str(tries))
                    response = self.recaptchaV2(url, website_key)
                    tries += 1
                else:
                    console("Recaptcha resolvido com sucesso")
                    tries = 4

            if tries == 4 and response == False:
                console("Após 4 tentativas não foi possível resolver o recaptcha")
                raise Exception("Após 4 tentativas não foi possível resolver o recaptcha de antecedentes criminais")

            console("Inserindo resposta do captcha no textArea...")
            console(response)
            self.wait_sleep(5)
            body = {
                "nome": name,
                "cpf": cpf,
                "googleRecaptcha": response,
                "nomeCaracteresEspeciais": name,
                "nomePaiCaracteresEspeciais": None,
                "nomeMaeCaracteresEspeciais": None
            }
            console(body)
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Content-Type": "application/json",
            }

            console('Enviando requisição...')
            response_api = requests.post(url_request, json= body, headers= headers)
            console("response status code: " + str(response_api.status_code)+"\n\n")

            if response_api.status_code == 201 :
                content = json.loads(response_api.content)
                console(content)
                self.data['found'] = True
                if content['nadaConsta'] == False :
                    console("alerta: encontrado")
                    self.data['nadaConsta'] = False
                    self.data['numeroCertidao'] =  content['numeroCertidao']
                    self.data['nome'] = name
                    self.data['cpf'] = cpf
                    self.data['alertas'] = 1
                else :
                    self.data['nadaConsta'] = True
                    self.data['numeroCertidao'] =  content['numeroCertidao']
                    self.data['nome'] = name
                    self.data['cpf'] = cpf
                    self.data['alertas'] = 0
            else:
                raise Exception('Consulta antecedentes criminais retornando status diferente de 201')

            write_results(json.dumps(self.data, ensure_ascii=False))
        except Exception as e:
            if retry < 4:
                console('Ocorreu um erro não esperando: ' + str(e))
                self.antecedentes(cpf, name, retry + 1)
            else:
                raise Exception(
                    'Erro após 5 tentativas de pegar os Antecedentes Criminais')
