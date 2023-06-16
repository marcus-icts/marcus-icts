from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import re
import json
import base64
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class CertidaoEmbargos(NewCoreLib.NewCoreLib):
    @keyword('Certidao Embargos - PF')
    def certificate_embargo_pf(self, cpf: str, retry: int = 0):
        try:
            console('\nTentativa ' + str(retry + 1) + ' de 5')

            cpf_formatted = re.sub('[^0-9]', '', cpf)

            url = 'https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php'

            doc_input_xpath = '//html/body/div[1]/div/div/div/div/div/div/div/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr[8]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr/td[2]/input'
            submit_button_xpath = '//html/body/div[1]/div/div/div/div/div/div/div/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr[8]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/button'

            console('Abrindo o Browser')
            self.open_browser(url, ignore_https_errors=True)

            self.wait_sleep(5)

            console('Digitando o CPF...')
            self.input_text(cpf_formatted, doc_input_xpath)

            self.wait_sleep(3)

            console('Iniciando o download do PDF...')
            with self.expect_download() as download_info:
                self.click_at(submit_button_xpath)

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

            self.teardown()

            write_results(json.dumps(self.data, ensure_ascii=False))
        except Exception as e:
            self.teardown()
            if retry < 4:
                console('Ocorreu um erro não esperando: ' + str(e))
                self.certificate_embargo_pf(cpf, retry + 1)
            else:
                raise Exception(
                    'Erro após 5 tentativas de pegar a Certidao Embargos - PF')

    @keyword('Certidao Embargos - PJ')
    def certificate_embargo_pj(self, cnpj: str, retry: int = 0):
        try:
            console('\nTentativa ' + str(retry + 1) + ' de 5')
            cnpj_formatted = re.sub('[^0-9]', '', cnpj)

            url = 'https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php'

            doc_input_xpath = '//html/body/div[1]/div/div/div/div/div/div/div/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr[8]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr/td[2]/input'
            submit_button_xpath = '//html/body/div[1]/div/div/div/div/div/div/div/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr[8]/td/table/tbody/tr/td/table/tbody/tr/td/div/div[2]/span/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/button'

            console('Abrindo o Browser')
            self.open_browser(url, ignore_https_errors=True)

            self.wait_sleep(5)

            console('Digitando o CNPJ...')
            self.input_text(cnpj_formatted, doc_input_xpath)

            self.wait_sleep(3)

            console('Iniciando o download do PDF...')
            with self.expect_download() as download_info:
                self.click_at(submit_button_xpath)

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
            self.teardown()
        except Exception as e:
            self.teardown()
            if retry < 4:
                console('Ocorreu um erro não esperando: ' + str(e))
                self.certificate_embargo_pj(cnpj, retry + 1)
            else:
                raise Exception(
                    'Erro após 5 tentativas de pegar a Certidao Embargos - PJ')
