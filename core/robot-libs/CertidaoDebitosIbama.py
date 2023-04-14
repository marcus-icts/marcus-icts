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
class CertidaoDebitosIbama(NewCoreLib.NewCoreLib):

    def resolveFormTab3(self, retry: int = 1):
        try:
            console('Resolvendo o form tab 3')
            confirm_input_xpath = '//*[@id="btnConfirmar"]'

            uf_select_xpath = '//*[@id="cad_cod_uf"]'
            name_input_xpath = '//*[@id="cad_nom_pessoa"]'
            address_input_xpath = '//*[@id="cad_end_pessoa"]'
            town_select_xpath = '//*[@id="cad_cod_municipio"]'
            neighborhood_input_xpath = '//*[@id="cad_des_bairro"]'

            self.input_text(
                'Certidão Negativa de Débito - IBAMA', name_input_xpath)

            self.wait_sleep(1)

            self.input_text('Teste', address_input_xpath)

            self.wait_sleep(1)

            self.input_text('Teste', neighborhood_input_xpath)

            self.wait_sleep(1)

            self.choose(uf_select_xpath, '12')

            self.wait_sleep(5)

            self.choose(town_select_xpath, '1200013')

            self.wait_sleep(5)

            with self.expect_download() as download_info:
                self.click_at(confirm_input_xpath)

            download = download_info.value
            data = open(download.path(), "rb").read()

            evidence_b64 = re.sub(
                r"\n", '', base64.encodebytes(data).decode('utf-8'))

            self.data['found'] = True
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(
                evidence_b64)

        except Exception as e:
            if retry < 6:
                console('Ocorreu um erro não esperando: ' + str(e))
                console('Tentativa ' + str(retry) + ' de 5 \n')
                self.resolveFormTab3(retry + 1)
            else:
                self.data['found'] = False
                raise Exception(
                    'Erro após 5 tentativas de resolver o form tab 3')

    def resolveFormTab2(self, retry: int = 1):
        try:
            console('Resolvendo o form tab 2')
            print_button_path = '//*[@id="gd_ln_1"]/td[4]/a'

            self.click_at(print_button_path)
        except Exception as e:
            if retry < 6:
                console('Ocorreu um erro não esperando: ' + str(e))
                console('Tentativa ' + str(retry) + ' de 5 \n')
                self.resolveFormTab2(retry + 1)
            else:
                self.data['found'] = False
                raise Exception(
                    'Erro após 5 tentativas de resolver o form tab 2')

    def resolveFormTab1(self, retry: int = 1):
        try:
            console('Resolvendo o form tab 1')
            print_button_path = '//*[@id="gd_ln_1"]/td[4]/a'

            console('Clicando no botão de impressão')
            self.click_at(print_button_path)

            self.wait_sleep(5)

            formMessage = self.query_selector(
                '//*[@id="dados"]/div/form/table/tbody/tr[2]/td/text()[1]')

            console(formMessage)

            self.wait_sleep(5000)

            console('Verificando se a mensagem "Consta débito" está visível')
            if formMessage.is_visible():
                console('A mensagem está visível')
                console('Tirando print da tela...')
                self.data['alertas'] = 1
                self.data['found'] = True
                self.data['evidence_type'] = 'image'
                self.data['evidence'] = self.take_evidence()
                return

            console('A mensagem não está visível')
            console('Iniciando o download do PDF...')
            with self.expect_download() as download_info:
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
            if retry < 6:
                console('Ocorreu um erro não esperando: ' + str(e))
                console('Tentativa ' + str(retry) + ' de 5 \n')
                self.resolveFormTab1(retry + 1)
            else:
                self.data['found'] = False
                raise Exception(
                    'Erro após 5 tentativas de resolver o form tab 2')

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
            raise Exception('resultado fora do esperado: Erro: ', e)

    @keyword('Certidao Debitos Ibama - PF')
    def certidao_debitos_ibama_pf(self, cpf: str):
        try:
            url = 'https://servicos.ibama.gov.br/sicafiext/sistema.php'

            input_xpath = '//*[@id="p_num_cpf_cnpj"]'
            search_input_xpath = '//*[@id="btnPesquisar"]'

            console('Abrindo o Browser')
            self.open_browser(url, False)

            self.wait_sleep(5)

            console('Executando script de emissão da certidão')
            self.page.evaluate(
                'javascript:menuWebSubmit("sisarr/cons_emitir_certidao")')

            self.wait_sleep(5)

            console('Digitando o documento')
            self.input_text(cpf, input_xpath)

            self.wait_sleep(5)

            console('Clicando no botão de pesquisa')
            self.click_at(search_input_xpath)

            self.wait_sleep(5)

            self.handleFormTab()

            console(self.data)

            self.wait_sleep(5000)

        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)
