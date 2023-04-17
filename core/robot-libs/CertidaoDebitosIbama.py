from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import re
import json
import base64
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class CertidaoDebitosIbama(NewCoreLib.NewCoreLib):

    def downloadPdfFormTab1(self, print_button_path: str):
        try:
            go_back_input_path = '//*[@id="btnVoltar"]'
            search_input_path = '//*[@id="btnPesquisar"]'
            document_input_path = '//*[@id="p_num_cpf_cnpj"]'

            console('Refazendo o fluxo de download do PDF')

            console('Voltando...')
            self.click_at(go_back_input_path)

            self.wait_sleep(5)

            console('Digitando o documento no input de pesquisa')
            self.input_text(self.doc, document_input_path)

            self.wait_sleep(3)

            console('Pesquisando...')
            self.click_at(search_input_path)

            self.wait_sleep(5)

            console('Iniciando o download do PDF...')
            with self.expect_download() as download_info:
                self.click_at(print_button_path)

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
        except Exception as e:
            raise Exception('Erro no downloadPdfFormTab1: ', e)

    def resolveFormTab3(self):
        try:
            console('Resolvendo o form tab 3')
            confirm_input_xpath = '//*[@id="btnConfirmar"]'

            uf_select_xpath = '//*[@id="cad_cod_uf"]'
            name_input_xpath = '//*[@id="cad_nom_pessoa"]'
            address_input_xpath = '//*[@id="cad_end_pessoa"]'
            town_select_xpath = '//*[@id="cad_cod_municipio"]'
            neighborhood_input_xpath = '//*[@id="cad_des_bairro"]'

            console('Preenchendo o input name')
            self.input_text(
                'Certidão Negativa de Débito - IBAMA', name_input_xpath)

            self.wait_sleep(3)

            console('Preenchendo o input endereço')
            self.input_text('Teste', address_input_xpath)

            self.wait_sleep(3)

            console('Preenchendo o input bairro')
            self.input_text('Teste', neighborhood_input_xpath)

            self.wait_sleep(3)

            console('Selecionando o UF')
            self.choose(uf_select_xpath, '12')

            self.wait_sleep(5)

            console('Selecionando o município')
            self.choose(town_select_xpath, '1200013')

            self.wait_sleep(5)

            console('Iniciando o download do PDF...')
            with self.expect_download() as download_info:
                self.click_at(confirm_input_xpath)

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

        except Exception as e:
            raise Exception('Erro no resolveFormTab3 ', e)

    def resolveFormTab2(self):
        try:
            console('Resolvendo o form tab 2')
            print_button_path = '//*[@id="gd_ln_1"]/td[4]/a'

            self.click_at(print_button_path)
        except Exception as e:
            raise Exception('Erro no resolveFormTab2: ', e)

    def resolveFormTab1(self):
        try:
            console('Resolvendo o form tab 1')
            print_button_path = '//*[@id="gd_ln_1"]/td[4]/a'

            console('Clicando no botão de impressão')
            self.click_at(print_button_path)

            self.wait_sleep(5)

            formMessage = self.page.locator(
                'text=Certidão não pode ser emitida pela Internet.')

            console('Verificando se a mensagem "Consta débito" está visível')
            if formMessage.count():
                console('A mensagem está visível')
                console('Tirando print da tela...')
                self.data['alertas'] = 1
                self.data['found'] = True
                self.data['evidence_type'] = 'image'
                self.data['evidence'] = self.take_evidence()
                return

            console('A mensagem não está visível')

            self.downloadPdfFormTab1(print_button_path)

        except Exception as e:
            raise Exception('Erro no resolveFormTab1: ', e)

    def handleFormTab(self):
        try:
            console('Tratando os form tab')

            formTab1 = self.query_selector('//*[@id="formDinAbaDados1"]')

            formTab2 = self.query_selector('//*[@id="formDinAbaDados2"]')

            formTab3 = self.query_selector('//*[@id="formDinAbaDados3"]')

            if formTab1.is_visible():
                console('O form tab 1 está visível')
                self.resolveFormTab1()

            if formTab2.is_visible():
                console('O form tab 2 está visível')
                self.resolveFormTab2()

            if formTab3.is_visible():
                console('O form tab 3 está visível')
                self.resolveFormTab3()

        except Exception as e:
            raise Exception('Erro no handleFormTab: ', e)

    @keyword('Certidao Debitos Ibama - PF')
    def certidao_debitos_ibama(self, doc: str, retry: int = 1):
        try:
            url = 'https://servicos.ibama.gov.br/sicafiext/sistema.php'

            self.doc = doc
            input_xpath = '//*[@id="p_num_cpf_cnpj"]'
            search_input_xpath = '//*[@id="btnPesquisar"]'

            console('Abrindo o Browser')
            self.open_browser(url, ignore_https_errors=True)

            self.wait_sleep(5)

            console('Executando script de emissão da certidão')
            self.page.evaluate(
                'javascript:menuWebSubmit("sisarr/cons_emitir_certidao")')

            self.wait_sleep(5)

            console('Digitando o documento')
            self.input_text(doc, input_xpath)

            self.wait_sleep(5)

            console('Clicando no botão de pesquisa')
            self.click_at(search_input_xpath)

            self.wait_sleep(5)

            self.handleFormTab()

            write_results(json.dumps(self.data, ensure_ascii=False))

            self.teardown()

        except Exception as e:
            if retry < 6:
                console('Ocorreu um erro não esperando: ' + str(e))
                console('Tentativa ' + str(retry) + ' de 5 \n')
                self.teardown()
                self.certidao_debitos_ibama(doc, retry + 1)
            else:
                raise Exception(
                    'Erro após 5 tentativas de pegar a Certdião de Débitos Ibama')
