from core.env import env
from utils import write_results
from robot.api.logger import console
from dataUriCaptcha import dataUriCaptcha
from robot.api.deco import keyword, library

import json
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class CertidaoReceitaFederalPj(NewCoreLib.NewCoreLib):
    @keyword('Certidao Receita Federal PJ')
    def certidao_receita_federal_pj(self, cnpj: str):
        try:
            url = 'https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir'
            input_cnpj = '//*[@id="NI"]'
            botao_validar = '//*[@id="validar"]'
            botao_segunda_via = '#FrmSelecao > a:nth-child(3)'
            tempo = 6
            self.open_browser(url)

            self.wait_sleep(tempo)

            self.input_text(cnpj, input_cnpj)

            self.wait_sleep(tempo)

            self.click_at(botao_validar)
            self.wait_sleep(tempo)
            popup = self.page.query_selector('body > div.ui-dialog.ui-corner-all.ui-widget.ui-widget-content.ui-front.ui-dialog-buttons.ui-draggable')
            if popup != None :
                console('entrei no caso de ter um popup')
                self.click_at(botao_validar)
            self.wait_sleep(tempo)

            check_possui_certidao = self.page.query_selector(botao_segunda_via)

            if check_possui_certidao != None:
                console('entrei pois possui segunda via')
                self.click_at('#FrmSelecao > a:nth-child(3)')

                self.wait_sleep(tempo)

                self.click_at(botao_validar)

                self.wait_sleep(tempo)
                self.data['found'] = True
                self.data['evidence'] = self.take_evidence()
                self.data['alerts'] = False
            else :
                console('entrei pois não possui segunda via então é caso positivo')
                self.wait_sleep(tempo)
                self.data['found'] = True
                self.data['evidence'] = self.take_evidence()
                self.data['alerts'] = True
            write_results(json.dumps(self.data, ensure_ascii=False))
            self.teardown()

        except Exception as e:
            self.teardown()
            raise Exception('resultado fora do esperado : Erro: ', e)
