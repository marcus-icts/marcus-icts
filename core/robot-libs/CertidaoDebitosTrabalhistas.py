from core.env import env
from utils import write_results
from robot.api.logger import console
from dataUriCaptcha import dataUriCaptcha
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import re
import json
import base64
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class CertidaoDebitosTrabalhistas(NewCoreLib.NewCoreLib):
    @keyword('Certidao Debitos Trabalhistas')
    def certidao_debitos_trabalhistas(self, doc: str, retry: int = 0):
        try:
            console('Tentativa ' + str(retry + 1) + ' de 5 \n')
            url = 'https://cndt-certidao.tst.jus.br/gerarCertidao.faces'

            captcha_image_xpath = '//*[@id="idImgBase64"]'
            doc_input_xpath = '//*[@id="gerarCertidaoForm:cpfCnpj"]'

            console('Abrindo o Browser')
            self.open_browser(url)

            self.wait_sleep(5)
            
            self.input_text(doc, doc_input_xpath)

            console('Resolvendo captcha de imagem')
            self.wait_for_element(captcha_image_xpath)
            card = self.query_selector(captcha_image_xpath)
            result = card.screenshot()

            console('Enviando print do captcha para o fornecedor')

            solver = dataUriCaptcha()
            solver.set_verbose(1)
            solver.set_key(env('CAPTCHA_KEY'))
            captcha_text = solver.solve_and_return_solution(
                base64.encodebytes(result))

            console(captcha_text)
            
            if captcha_text != 0:
               captcha_input_xpath = '//*[@id="idCampoResposta"]'
               input_submit_xpath = '//*[@id="gerarCertidaoForm:btnEmitirCertidao"]'

               self.input_text(captcha_text, captcha_input_xpath)

               console('Iniciando o download do PDF...')
               with self.expect_download() as download_info:
                    self.click_at(input_submit_xpath)

               download = download_info.value

               data = open(download.path(), "rb").read()
               console('PDF baixado com sucesso')

               console('Covertendo PDF para base64')
               evidence_b64 = re.sub(
                    r"\n", '', base64.encodebytes(data).decode('utf-8'))

               console('Conversão realizada com sucesso')
               self.data['found'] = True
               self.data['evidence_type'] = 'pdf'
               self.data['evidence'] = 'data:application/pdf;base64,{}'.format(
                    evidence_b64)
               
               write_results(json.dumps(self.data, ensure_ascii=False))
            else:
                raise Exception(
                    'Não houve retorno da resolução do captcha')

            
        except Exception as e:
            if retry < 4:
                console('Ocorreu um erro não esperando: ' + str(e))
                self.teardown()
                self.certidao_debitos_trabalhistas(doc, retry + 1)
            else:
                raise Exception(
                    'Erro após 5 tentativas de pegar a Certidao Debitos Trabalhistas')
