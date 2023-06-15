from robot.api.deco import keyword, library
from robot.api.logger import console
from utils import write_results
import json, re, base64
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class Trf4(NewCoreLib.NewCoreLib):
    @keyword('trf4')
    def execute_trf4(self, documento: str, tipo_certidao: str, retry: int = 0):
        url = 'https://www2.trf4.jus.br/trf4/processos/certidao/index.php'
        console("Abrindo navegador...")
        self.open_browser("https://www2.trf4.jus.br/trf4/processos/certidao/index.php")

        campo_documento = '//*[@id="string_cpf"]'
        website_key = '6Ldv-vIUAAAAAN2v6GbNs9w5HTS0HTTLhFL8dDB8'

        self.wait_sleep(3)

        console("Digitar documento")
        self.input_text(documento, campo_documento)
        self.wait_sleep(3)

        console("Selecionando tipo de certidão")
        self.click_at(tipo_certidao)
        self.wait_sleep(3)

        try:
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
                raise Exception("Após 4 tentativas não foi possível resolver o recaptcha")

            console("Inserindo resposta do captcha no textArea...")
            self.page.eval_on_selector('#g-recaptcha-response', '(el) => el.value =' +"'"+ response +"'")

            self.wait_sleep(5)
            self.page.query_selector('//*[@id="botaoEmitir"]').click()
            self.wait_sleep(10)

            console('Analisando resultado...')
            check_certidao = self.page.query_selector('body > strong:nth-child(1)')

            if check_certidao == None:
                self.data['found'] = True
                str_check= '//*[@id="formulario_solicitacao"]/p[1]'
                check_processo = self.page.query_selector(str_check)
                # console(check_processo)
                if check_processo and (
                    self.page.query_selector(str_check).inner_text() == 'ATENÇÃO: NÃO FOI POSSÍVEL EMITIR A CERTIDÃO JUDICIAL CÍVEL'
                    or self.page.query_selector(str_check).inner_text() == 'ATENÇÃO: NÃO FOI POSSÍVEL EMITIR A CERTIDÃO JUDICIAL CRIMINAL'
                    or self.page.query_selector(str_check).inner_text() == 'ATENÇÃO: NÃO FOI POSSÍVEL EMITIR A CERTIDÃO JUDICIAL PARA FINS ELEITORAIS'
                ):
                    console("Não foi possível emitir certidão por possível resultado de alerta")
                    data = self.page.query_selector('//*[@id="divDetalhesPoliticaPrivacidade"]')
                    if data != None :
                        self.page.evaluate('document.querySelector("#divDetalhesPoliticaPrivacidade").remove()')
                    self.data['evidence'] = self.take_evidence()
                    self.data['alertas'] = 1
                else :
                    console("Certidão negativa emitida")
                    with self.page.expect_download() as download_info:
                        self.page.query_selector('//*[@id="botaoVisualizar"]').click()
                    download = download_info.value
                    # console(download.path())
                    data = open(download.path(), "rb").read()
                    evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
                    # console(evidence_b64)
                    self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
                    self.data['alertas'] = 0
            else :
                console('Tentando novamente, ocorreu um erro inesperado')
                if retry < 3:
                    self.teardown()
                    self.execute_trf4(documento, tipo_certidao, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    raise Exception('Erro após 4 tentativas')

            self.wait_sleep(5)
            write_results(json.dumps(self.data, ensure_ascii=False))
            self.teardown()

        except Exception as e:
            self.teardown()
            raise Exception('Erro: ', e)
