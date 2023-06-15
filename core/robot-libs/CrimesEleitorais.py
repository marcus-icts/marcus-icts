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
            url = 'https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-crimes-eleitorais'
            campo_nome_eleitor = '//*[@id="CE_NomeEleitor"]'
            campo_cpf = '//*[@id="CE_NumeroTituloCPF"]'
            campo_data_nascimento = '//*[@id="CE_DataNascimento"]'
            campo_nao_consta_mae = '//*[@id="CE_NaoConstaMae"]'
            campo_nao_consta_pai = '//*[@id="CE_NaoConstaPai"]'
            campo_mae = '//*[@id="CE_NomeMae"]'
            campo_pai = '//*[@id="CE_NomePai"]'
            btn_emitir = '//*[@id="form-crimes-eleitorais"]/fieldset/button'
            nome_pai = nome_pai if nome_pai != '' else 'NAO CONSTA'
            nome_mae = nome_mae if nome_mae != '' else 'NAO CONSTA'

            self.open_browser(url)
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
                console("Preenchendo o nome da mãe")
                self.input_text(nome_pai, campo_pai)

            self.wait_sleep(1)

            console('revalidando token recaptcha..')
            self.page.evaluate("let captcha_response = 'g-recaptcha-' + $(form).attr('id');grecaptcha.ready(function(){grecaptcha.execute('6LeEYa0fAAAAAIwHU9lHw3fahlRNNb6yvv1Fjnbc', {action: '7fb57b96068b49c17ea252cf53024f00'}).then(function(token){if ( $( '#' + captcha_response ).length ) {$( '#' + captcha_response ).val(token);}else{$(form).prepend($('<input>', {type: 'hidden',id: captcha_response,name: captcha_response,value: token}));};});});")
            self.wait_sleep(2)

            console('Esperando download da certidão')
            with self.page.expect_download() as download_info:
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
            self.teardown()
            if (self.page.query_selector('//*[@id="ancora-1"]/div/div[1]') != None):
                console('Certidão não emitida')
                self.wait_sleep(1)
                self.data['evidence'] = self.take_evidence()
                self.data['found'] = True
                self.data['evidence_type'] = 'image'
                self.wait_sleep(2)
                write_results(json.dumps(self.data, ensure_ascii=False))
            else:
                raise Exception('resultado fora do esperado. erro: ', str(e))
