from core.env import env
from utils import write_results
from robot.api.logger import console
from dataUriCaptcha import dataUriCaptcha
from robot.api.deco import keyword, library

import json
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class ConsultaMexico(NewCoreLib.NewCoreLib):
    @keyword('Consulta Mexico')
    def consulta_mexico(self, cnpj: str):
        try:
            url = 'https://cnet.hacienda.gob.mx/servicios/consultaRUPC.jsf'
            input_cnpj = '//*[@id="consulta:razon"]'
            botao_validar = '//*[@id="consulta:btnBuscar"]'

            tempo = 6
            self.open_browser(url, False, 1000)

            self.wait_sleep(tempo)

            self.click_at('//*[@id="consulta:tipoSol"]/div[2]')

            self.wait_sleep(2)

            self.click_at('//*[@id="consulta:tipoSol_panel"]/div/ul/li[2]')

            self.wait_sleep(3)
            self.input_text(cnpj, input_cnpj)

            self.wait_sleep(tempo)

            self.click_at(botao_validar)

            self.wait_sleep(15)
            self.data['found'] = True
            self.data['resultados'] = []
            resultado_bruto = self.page.query_selector('//*[@id="formTabla:tabla"]/table/tfoot/tr[2]/td').inner_text()
            resultados = resultado_bruto.split(": ")
            total_resultados = int(resultados[1])
            console(total_resultados)

            resultados_totais_lidos = 0
            if total_resultados > 0 :
                self.data['alerts'] = True
                percorre_loop = True
            else :
                self.data['alerts'] = False
                percorre_loop = False

            while(percorre_loop) :
                cases = self.page.query_selector_all('//*[@id="formTabla:tabla_data"]/tr')
                for case in cases:
                    resultados_totais_lidos += 1
                    dados = {}
                    console('pegando dados da linha')
                    console(case.query_selector('td:nth-child(1)'))
                    dados['razao_social'] = case.query_selector('td:nth-child(1)').inner_text()
                    dados['titularidade'] = case.query_selector('td:nth-child(2)').inner_text()
                    dados['entidade'] = case.query_selector('td:nth-child(3)').inner_text()
                    console('clicando no span')
                    case.query_selector('td:nth-child(5)').click()
                    console('depois de clicar no span')
                    self.wait_sleep(1)
                    dados['pais'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[2]/td[2]').inner_text()
                    dados['tamanho'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[4]/td[2]').inner_text()
                    dados['tipo_usuario'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[5]/td[2]').inner_text()
                    dados['setor'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[6]/td[2]').inner_text()
                    dados['giro'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[7]/td[2]').inner_text()
                    dados['site'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[8]/td[2]').inner_text()
                    dados['baixa'] = self.page.query_selector('//*[@id="formTabla:j_idt74"]/tbody/tr[9]/td[2]').inner_text()
                    self.page.query_selector('//*[@id="formTabla:btnCerrar"]').click()
                    console(dados)
                    self.data['resultados'].append(dados)
                if total_resultados > resultados_totais_lidos :
                    self.page.query_selector('//*[@id="formTabla:tabla_paginator_top"]/span[4]/span').click()
                    self.wait_sleep(4)
                else :
                    percorre_loop = False

            write_results(json.dumps(self.data, ensure_ascii=False))
            self.teardown()

        except Exception as e:
            self.teardown()
            raise Exception('resultado fora do esperado : Erro: ', e)
