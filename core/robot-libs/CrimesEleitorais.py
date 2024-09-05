from robot.api.deco import keyword, library
from robot.api.logger import console
from utils import write_results
import json, re, base64
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class CrimesEleitorais(NewCoreLib.NewCoreLib):
    @keyword('crimes eleitorais')
    def abrir_crimes_eleitorais_para_evidencia(self, nome: str, cpf: str, data_nascimento: str, nome_mae: str = '', nome_pai: str = ''):
        try:
            btn_selecionar_crimes_eleitorais = '#content > app-root > div > app-certidoes > div:nth-child(3) > app-menu-option:nth-child(2) > button'
            wait_timeout = 30000
            url = 'https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral#/certidoes-eleitor'
            btn_selecionar_crimes_eleitorais = '#content > app-root > div > app-certidoes > div:nth-child(3) > app-menu-option:nth-child(2) > button'
            campo_nome_eleitor = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.form-container > div.form-group-nome > input'
            campo_cpf = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.form-container > div.form-group-titulo-cpf > input'
            campo_data_nascimento = '//*[@id="modal"]/div/div/div[2]/div[2]/form/div[1]/div[3]/input'
            campo_nao_consta_mae = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.form-container > div.form-group-nome-mae > div > span > input'
            campo_nao_consta_pai = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.form-container > div.form-group-nome-pai > div > span > input'
            campo_mae = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.form-container > div.form-group-nome-mae > div > input'
            campo_pai = '#nomePai'
            btn_emitir = '#modal > div > div > div.modal-corpo > div.login-form-row > form > div.menu-botoes > button.btn-tse'
            nome_pai = nome_pai if nome_pai != '' else 'NAO CONSTA'
            nome_mae = nome_mae if nome_mae != '' else 'NAO CONSTA'

            self.open_browser(url)
            self.click_at(btn_selecionar_crimes_eleitorais)
            self.wait_sleep(5)

            console('Removendo modal lgpd')
            self.page.evaluate("document.querySelector('#modal-lgpd').remove()")

            self.input_text(nome, campo_nome_eleitor)
            self.input_text(cpf, campo_cpf)
            self.input_text(data_nascimento, campo_data_nascimento)
            self.wait_sleep(3)

            if nome_mae == 'NAO CONSTA':
                console("Clicando no botão 'Não consta' para o nome da mãe")
                self.click_at(campo_nao_consta_mae)
            else:
                console("Preenchendo o nome da mãe")
                self.input_text(nome_mae, campo_mae)

            if nome_pai == 'NAO CONSTA':
                console("Clicando no botão 'Não consta' para o nome do pai")
                self.click_at(campo_nao_consta_pai)
            else:
                console("Preenchendo o nome do pai")
                self.input_text(nome_pai, campo_pai)

            self.wait_sleep(5)

            console('Esperando download da certidão')
            with self.page.expect_download(timeout=wait_timeout) as download_info:
                console("Clicando no botão de emitir")
                self.click_at(btn_emitir)
                self.wait_sleep(15)
            download = download_info.value
            data = open(download.path(), "rb").read()
            evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            console(evidence_b64)
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            self.data['found'] = True
            self.data['evidence_type'] = 'pdf'

            self.wait_sleep(2)
            write_results(json.dumps(self.data, ensure_ascii=False))
            self.wait_sleep(2)
            self.teardown()
        except Exception as e:
            if (self.page.query_selector('//*[@id="ancora-1"]/div/div[1]') != None):
                console('Certidão não emitida')
                self.wait_sleep(1)
                self.data['evidence'] = self.take_evidence()
                self.data['found'] = True
                self.data['evidence_type'] = 'image'
                self.wait_sleep(2)
                write_results(json.dumps(self.data, ensure_ascii=False))
                self.teardown()
            else:
                self.teardown()
                raise Exception('resultado fora do esperado. erro: ', str(e))
