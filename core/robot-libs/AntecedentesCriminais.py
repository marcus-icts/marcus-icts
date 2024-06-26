from utils import write_results
from robot.api.logger import console
from robot.api.deco import keyword, library
from anticaptchaofficial.recaptchav2proxyless import *
from pypdf import PdfReader
from datetime import datetime

import re, json, requests, base64, tempfile, os
import NewCoreLib


@library(scope='GLOBAL', version='0.0.1')
class AntecedentesCriminais(NewCoreLib.NewCoreLib):
    @keyword('Antecedentes Criminais')
    def antecedentes(self, cpf: str, nome: str, nascimento:str, mae: str = None, retry: int = 0):
        try:
            console('\nTentativa ' + str(retry + 1) + ' de 5')
            
            url_validar_dados = 'https://servicos.pf.gov.br/sinic2-publico-rest/api/cac/validar-dados-cac'
            console('Consultando validade da documentação, aguarde.')

            cpf = re.sub('\D', '', cpf)
            formatted_nascimento = datetime.strptime(nascimento, "%d/%m/%Y")
            formatted_nascimento = formatted_nascimento.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            body_validar_dados = {
                "cpf": cpf,
                "dtNascimento": formatted_nascimento,
                "nome": nome
            }

            if mae != None:
                body_validar_dados['nomeMae'] = mae

            headers_validar_dados = {
                "Accept": "application/json; charset=utf-8", 
                "Content-Type": "application/json",
            }

            response_validar_dados = requests.post(url_validar_dados, json = body_validar_dados, headers = headers_validar_dados)
            response_validar_dados_content = json.loads(response_validar_dados.content)

            if response_validar_dados_content['dadosValidosReceita'] == False:
                raise Exception('Dados insuficientes ou inválidos, verifique.{}'
                                    .format(json.dumps(body_validar_dados, ensure_ascii = False)))

            url = 'https://servicos.pf.gov.br/epol-sinic-publico/'
            url_emitir_cac = 'https://servicos.pf.gov.br/sinic2-publico-rest/api/cac/gerar-cac-pdf'
            website_key = '6Le9QFkUAAAAAEtyzsbIZUcFbq8pT4KvKghL6Zb0'

            console("Resolvendo recaptcha v2")
            response = self.recaptchaV2(url, website_key)
            tries = 1
            
            data = {}
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
                raise Exception("Após 4 tentativas não foi possível resolver o recaptcha de antecedentes criminais")

            console(response)
            self.wait_sleep(5)
            
            body = {
                "nome": nome,
                "cpf": cpf,
                "listaNacionalidade": None,
                "dtNascimento": formatted_nascimento,
                "coPaisNascimento": None,
                "noUfNascimento": None,
                "noMunicipioNascimento": None,
                "ufNascimento": None,
                "coMunicipioNascimento": None,
                "nomePai": "",
                "nomeMae": "",
                "documentoCac": [],
                "stPossuiMae": False
            }

            if mae != None:
                body['nomeMae'] = mae
                body['stPossuiMae'] = True
                console('Nome da mãe informado.')

            console(body)
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Token.Recaptcha.Google": response,
                "Content-Type": "application/json",
            }

            console('Enviando requisição...')
            response_api = requests.post(url_emitir_cac, json= body, headers= headers)
            console("StatusCode: " + str(response_api.status_code)+"\n\n")

            if response_api.status_code == 200 :
                content = json.loads(response_api.content)
                # console(content)
                data['found'] = True
                data['nome'] = nome
                data['cpf'] = cpf
                data['nr_protocolo'] =  content['nrProtocolo']
                data['evidence_type'] = 'pdf'
                data['evidence'] = "data:application/pdf;base64,{}".format(content['pdf'])

                pdf_data = base64.b64decode(content['pdf'])

                # Criar um arquivo temporário
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                    temp_pdf.write(pdf_data)
                    temp_pdf_path = temp_pdf.name

                console("Arquivo PDF salvo temporariamente em: {}".format(temp_pdf_path))

                with open(temp_pdf_path, "rb") as file:
                    reader = PdfReader(file)
                    number_of_pages = len(reader.pages)
                    pdf_text = ""
                    
                    for page_num in range(number_of_pages):
                        page = reader.pages[page_num]
                        pdf_text += page.extract_text()
                
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                    console("Arquivo temporário deletado.")

                console("Conteúdo do PDF extraído:")
                console(pdf_text)

                nada_consta_str = 'NÃO CONSTA condenação'

                if nada_consta_str.lower() in pdf_text.lower():
                    data['nadaConsta'] = True
                    data['alertas'] = 0
                else:
                    data['nadaConsta'] = False
                    data['alertas'] = 1

            else:
                raise Exception('Consulta antecedentes criminais retornando status diferente de 200')
            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            if retry < 4:
                console('Ocorreu um erro não esperando: ' + str(e))
                self.antecedentes(cpf, nome, nascimento, mae, retry + 1)
            else:
                raise Exception('Erro após 5 tentativas de pegar os Antecedentes Criminais')
