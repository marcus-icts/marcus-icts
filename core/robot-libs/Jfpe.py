from core.env import env
from utils import write_results
from robot.api.logger import console
from dataUriCaptcha import dataUriCaptcha
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import os
import re
import json
import base64
import requests
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class Jfpe(NewCoreLib.NewCoreLib):
    def solve_captcha_image_jfpe(self, selector: str, input: str, click: str, retry: int = 0):
        console('Resolvendo captcha Imagem')
        data = {}
        self.wait_for_element(selector)
        card = self.query_selector(selector)
        result = card.screenshot()
        
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))
        
        if captcha_text != 0:
            console("captcha text " + captcha_text)
            self.input_text(captcha_text, input)

            self.query_selector(click).click()
            self.wait_sleep(30)
            try:
                dialog = self.query_selector('//*[@id="form:dialogCertidaoDistribuicao1_content"]')
                
                if dialog.is_visible():
                    console('captcha funcionou')
            except Exception as e:
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                console(str(e))
                if retry < 3:
                    self.solve_captcha_image_jfpe(selector, input, click, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    data['found'] = False
                    raise Exception('Erro após 4 tentativas de resolver o captcha')
        else:
            raise Exception('Erro na comunicação com o fornecedor de resolver captcha')
         
    def download_jfpe(self):
        self.wait_sleep(15)
        self.data['found'] = True
        check_process = self.query_selector('//*[@id="form:j_idt173"]')
        check_ok = self.query_selector('//*[@id="form:j_idt159"]')
        # process.env.DEBUG = 'pw:api,pw:browser*'
        if check_process.is_visible():
            console('tem processo')
            self.data['alertas'] = 1
            self.data['result'] = self.query_selector('//*[@id="form:labelTipoRetorno3"]').inner_text()
            self.wait_sleep(20)
            with self.expect_download() as download_info:
                self.query_selector('//*[@id="form:j_idt173"]').click()
            download = download_info.value
            data = open(download.path(), "rb").read()
            evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            write_results(json.dumps(self.data, ensure_ascii=False))
        elif check_ok.is_visible():
            self.data['alertas'] = 0
            self.wait_sleep(20)
            with self.expect_download() as download_info:
                self.query_selector('//*[@id="form:j_idt159"]').click()
            download = download_info.value
            data = open(download.path(), "rb").read()
            evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            write_results(json.dumps(self.data, ensure_ascii=False))
        else :
            raise Exception('resultado fora do esperado')
  
    @keyword('JFPE - PF')
    def federal_justice_of_pernambuco_pf(self, cpf: str):
        try:
            url = 'https://certidoes.trf5.jus.br/certidoes2022/paginas/certidaodistribuicaoparte.faces'
            
            button_path = '//*[@id="j_idt11"]'
            form_path = '//*[@id="form:captcha"]'    
            input_path = '//*[@id="form:cpfCnpj"]'
            jform_path = '//*[@id="form:jcaptcha"]'  
            select_path = '//*[@id="form:orgaoInternet"]'
            panel_path = '//*[@id="form:padPanel_content"]'
            form_validate_path = '//*[@id="form:validar"]/span'
            
            self.open_browser(url, False)

            self.wait_sleep(5)
      
            self.choose(select_path, '5')
            
            self.wait_sleep(1)
            
            self.input_text(cpf, input_path)
            
            self.wait_sleep(1)
            
            self.click_at(panel_path)
            
            self.wait_sleep(5)
            
            self.click_at(button_path)
            
            self.wait_sleep(5)
            
            self.solve_captcha_image_jfpe(form_path, jform_path, form_validate_path)
            
            self.download_jfpe()
            
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)

    @keyword('JFPE - PJ')
    def federal_justice_of_pernambuco_pj(self, cnpj: str):
        try:
            url = 'https://certidoes.trf5.jus.br/certidoes2022/paginas/certidaodistribuicaoparte.faces'
            
            button_path = '//*[@id="j_idt15"]'
            form_path = '//*[@id="form:captcha"]'    
            input_path = '//*[@id="form:cpfCnpj"]'
            jform_path = '//*[@id="form:jcaptcha"]'  
            select_path = '//*[@id="form:orgaoInternet"]'
            panel_path = '//*[@id="form:padPanel_content"]'
            form_validate_path = '//*[@id="form:validar"]/span'
            
            self.open_browser(url, False)

            self.wait_sleep(5)
      
            self.choose(select_path, '5')
            
            self.wait_sleep(1)
            
            self.input_text(cnpj, input_path)
            
            self.wait_sleep(1)
            
            self.click_at(panel_path)
            
            self.wait_sleep(5)
            
            self.click_at(button_path)
            
            self.wait_sleep(5)
            
            self.solve_captcha_image_jfpe(form_path, jform_path, form_validate_path)
            
            self.download_jfpe()
        except Exception as e:
            raise Exception('resultado fora do esperado: Erro: ', e)
    