from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *
from robot.libraries.BuiltIn import BuiltIn

import re
import json
import base64
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class AntecedentesCriminais(NewCoreLib.NewCoreLib):
    @keyword('Antecedentes Criminais')
    def antecedentes(self, cpf: str, nome: str, nascimento: str, mae: str = None, retry: int = 0):
        # try:

            console('\nTentativa ' + str(retry + 1) + ' de 5')
            
            url = 'https://servicos.pf.gov.br/epol-sinic-publico/'
            recaptcha_sitekey = "6Le9QFkUAAAAAEtyzsbIZUcFbq8pT4KvKghL6Zb0"

            self.open_browser(url, False, ignore_https_errors=True)

            cpf_input_selector = 'pf-input-cpf input[type="text"]'            
            self.wait_for_element(cpf_input_selector)

            # insere o CPF

            sanitized_cpf = re.sub('\D', '', cpf)
            self.input_text(sanitized_cpf, cpf_input_selector)
            self.wait_sleep(3)

            # insere o nome
            nome_input_selector = 'input[formcontrolname="nome"]'
            self.input_text(nome, nome_input_selector)
            self.wait_sleep(3)
            
            # entra com a data atraves do datepicker
            self.datepicker_manipulate(nascimento)

            # se nao tiver o nome da mae, desativa o campo
            if mae != None :
                mae_input_selector = 'input[formcontrolname="nomeMae"]'
                self.input_text(mae, mae_input_selector)
                self.wait_sleep(3)
            else:
                nome_mae_switch_selector = 'p-inputswitch#swt-possui-mae div'
                self.click_at(nome_mae_switch_selector)
            
            self.wait_sleep(3)
            
            submit_button_selector = 'button#btn-emitir-cac'
            self.click_at(submit_button_selector)
            
            self.wait_sleep(5)

            # alerta de dados incorretos
            incorrect_data_alert_selector = 'div.p-message.p-message-warn'
            incorrect_data_alert = self.query_selector(incorrect_data_alert_selector)

            if incorrect_data_alert != None:
                message = self.query_selector(incorrect_data_alert_selector + " div span.p-message-detail").inner_text()
                raise Exception(message)

            console("Resolvendo RECAPTCHA v2")

            self.page.eval_on_selector('p-dynamicdialog button#btn-ok', '(el) => el.disabled = false')
            recaptcha_iframe_name = self.page.locator('iframe[title="reCAPTCHA"]').get_attribute("name")
            recaptcha_iframe = self.page.frame(name = recaptcha_iframe_name)
            recaptcha_iframe.query_selector("div.recaptcha-checkbox-border").click()
            self.wait_sleep(5)
            s = recaptcha_iframe.locator("span#recaptcha-anchor")

            if s.get_attribute("aria-checked") == "false":
                recaptcha_response = self.recaptchaV2(url, recaptcha_sitekey)
                recaptcha_tries = 1
                while recaptcha_tries < 4:
                    if recaptcha_response == False:
                        console("Problema na resolução do RECAPTCHA. Tentativa número " + str(recaptcha_tries))
                        recaptcha_response = self.recaptchaV2(url, recaptcha_sitekey)
                        recaptcha_tries += 1
                    else:
                        console("RECAPTCHA resolvido com sucesso")
                        recaptcha_tries = 4

                if recaptcha_tries == 4 and recaptcha_response == False:
                    console("Após 4 tentativas não foi possível resolver o RECAPTCHA")
                    raise Exception("Após 4 tentativas, não foi possível resolver o RECAPTCHA")

                console("Inserindo resposta do captcha no textArea...")
                self.page.eval_on_selector('#g-recaptcha-response', "(el) => el.value ='" + recaptcha_response + "'")

            self.wait_sleep(30)
            self.page.query_selector('p-dynamicdialog button#btn-ok').click()
            BuiltIn().sleep('2000ms')

            console('Iniciando o download do PDF...')
            
            self.data['found'] = False

            with self.expect_download() as download_info:
                download = download_info.value
                data = open(download.path(), "rb").read()
                console('PDF baixado com sucesso, convertendo para base64...')
                evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
                console('Conversão realizada com sucesso')
                self.data['found'] = True
                self.data['evidence_type'] = 'pdf'
                self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            
            write_results(json.dumps(self.data, ensure_ascii=False))
        # except Exception as e:
            # if retry < 4:
            #     console('Ocorreu um erro não esperando: ' + str(e))
            #     self.antecedentes(cpf, nome, nascimento, retry + 1)
            # else:
            #     raise Exception('Erro após 5 tentativas de pegar os Antecedentes Criminais')
            
            self.teardown()

    def datepicker_manipulate(self, nascimento: str):
        datepicker_modal_selector = "div.pf-datepicker.pf-component"
        datepicker_previous_button_selector = datepicker_modal_selector + " button.pf-datepicker-prev"
        datepicker_title_selector = datepicker_modal_selector + " div.pf-datepicker-title"
        datepicker_month_selector = datepicker_title_selector + " span.pf-datepicker-month"
        datepicker_year_selector = datepicker_title_selector + " span.pf-datepicker-year"
        datepicker_days_table_selector = datepicker_modal_selector + " table.pf-datepicker-calendar"
        
        console('Abrindo datepicker...')

        self.query_selector("pf-calendar button.pf-datepicker-trigger").click()

        self.wait_for_element(datepicker_modal_selector)

        months = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        day, month, year = nascimento.split('/')
    
        day = int(day)
        month = int(month)
        month_text = months[ month - 1]

        while True:
            current_month = self.query_selector(datepicker_month_selector).inner_text()
            current_year = self.query_selector(datepicker_year_selector).inner_text()

            if current_year == '1900':
                console('Data não encontrada.')
                break

            # console("mes: " + current_month + ", ano: " + current_year + ", verificando...")

            if current_year == year and current_month.lower() == month_text.lower():

                days_selector = datepicker_days_table_selector + " tbody > tr td:not(.pf-datepicker-other-month) span"
                clickable_days = self.page.query_selector_all(days_selector)

                for clickable_day in clickable_days:
                    day_value = clickable_day.inner_text()
                    
                    if day_value == str(day):
                        clickable_day.click()
                        console('Data selecionada.')
                        return

                console('Data não encontrada, houve algum problema.')
                return
            
            self.query_selector(datepicker_previous_button_selector).click()