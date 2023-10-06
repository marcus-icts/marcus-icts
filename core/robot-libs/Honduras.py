from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *

import json, re, base64, requests
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class Honduras(NewCoreLib.NewCoreLib):
    @keyword('Buscar resultado honduras')
    def buscarResultadoHonduras(self, name: str):
        data = {}
    
        url = 'https://oncae.gob.hn/certificaciones#bfaccordion-70-slider-0'
        console("Abrindo navegador")
        self.open_browser(url)
        data['found'] = False
        self.wait_sleep(2)

        console("Buscando lista de elementos")
        acordion = self.page.query_selector_all('div.phocadownloadfilelist')
        pdfs = acordion[0].query_selector_all('.phocadownloadfilelistitem')
        self.wait_sleep(2)
        qtd = 1
        results = []
        for pdf in pdfs:
            pdf_link = pdf.query_selector('.pd-document64 > a')
            name_found = pdf.query_selector('.pd-document64 > a').inner_text()
            console("Verificando compatibilidade dos dados pesquisados com o resultado encontrado")
            if name.upper() in name_found.upper() and qtd <= 20:
                qtd = qtd + 1
                data['found'] = True
                registro = str(re.search("[0-9]{4}-[0-9]{4}", name_found).group())
                result = {
                    "name_found": name_found.replace(registro, ""),
                    "pdf_url": 'https://oncae.gob.hn' + pdf_link.get_attribute('href'),
                    "registro": registro
                    }
                results.append(result)

        console("Preparando o download das evidencias")       
        for result in results:
            response = requests.get(result['pdf_url'])
            if response.status_code == 200:
                console("Download coletado com sucesso")
                pdf_content = response.content
                evidence_b64 = base64.b64encode(pdf_content).decode('utf-8')
                result['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
                self.wait_sleep(1)

            # TRECHO DE CÓDIGO QUE NÃO FUNCIONAVA EM INT (PARA AVALIAR FUTURAMENTE)
            # with self.page.expect_download() as download_info:
            #     console(result['pdf_url'])
            #     self.page.goto(result['pdf_url'])
            #     self.wait_sleep(2)
            # download = download_info.value
            # file = open(download.path(), "rb").read()
            # evidence_b64 = re.sub(r"\n", '', base64.encodebytes(file).decode('utf-8'))
            
                
        
        data['results'] = results
        data['qtd'] = len(data['results'])
        console(json.dumps(data, ensure_ascii=False, indent=4))
                
        write_results(json.dumps(data, ensure_ascii=False))
        self.wait_sleep(1)
        self.teardown()