from robot.api.deco import keyword, library
from robot.api.logger import console
from utils import write_results
import json, requests
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class QuitacaoEleitoral(NewCoreLib.NewCoreLib):
    @keyword('quitacao eleitoral')
    def quitacao_eleitoral(self, nome: str, cpf: str, data_nascimento: str, nome_mae: str = '', nome_pai: str = ''):
        try:
            msg_dados_invalidos = 'Os dados informados (nome, data de nascimento ou filiação) não conferem com aqueles constantes do Cadastro Eleitoral.'
            msg_doc_invalido = 'Título de eleitor inválido'
            msg_recaptcha = 'A validação do reCAPTCHA falhou.'
            nome_pai = nome_pai if nome_pai != '' else 'NAO CONSTA'
            nome_mae = nome_mae if nome_mae != '' else 'NAO CONSTA'
            data = {}
            textNaoQuite = "abaixo qualificado(a) não está quite"
            url_site = 'https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-quitacao-eleitoral'
            url = 'https://www.tse.jus.br/@certidao-quitacao'
            body = {
                'token':'03AFY_a8Xk9JUcRm6eavVbw9DAeiWz1UaTDFckDBFPxeLjKMVwThJOBKkQySNjzdDERS_1nZ-EMt2iOjTOic_aiyJvLc_SqSkdE3tjzQNi8MBXLDAlAZWQhR9W3blyXqNFHz3FS6fCe7tf_2SeqgyBb6DJyRTVRbYUc4z7AOFdbaxuLqqk0Cp51xdVD9NVtIfXv5ul26ouXgZe2MjBPtrEWqC8ICf_whQXS4oYOvBzMMoCvg48QGPFqQtbYh4LkIUVzi2X4IYUW5BMJcdxa4fkwV15Vt3SeOEzxYVcNaH-Id1FTdZIW-hMO2v4tX0gqPj45JWPW0T7rz4dV4yYxU88vjTlfSBZJny-TFGwjAVKC3ntPK66WdfUKd3CqyntpAvmWAUiwmQWXyIuyuFG57mhxCtQn_fOr9ag4mC308uVQrL_nw3WRgjyiikrlxsh28ZeLLPzQWHcYDuMpTW5zRKEeGXsP37F2DDPH6HhMTSZN5xnISRmrMlT_qIHRLFEdPoBpZ_PWQY_bvGi8hESXkt8Yh2QT2A15SVrmL2IAFjgAYgyDGctC_Rq2pb1n_Z7dq9i5GNJndIF2aPP_Gc84cSQ8EAMFZrb7IP_xc9v3DOOtu_ReH-9QB5RkkZ7mwD126QXs0DVIUIBkiQNdD5TwwH5D3LrpfK1x8-oTq02O2UBD-cOf0NrHcy92MUCwWqX0V1jywB7QOoqPOrPbGWExg4jrlLFIsVKU1sLS5Cu6SqqT6XR50juNNzqWetrVI7oARIwXHcsvI5cmFUh1WkNZkVbCCzumRpmMuit8Tq7YfT5-BaUM52TGCNTB3qS8AYilGbIQeg0P4_tVHFph-P1qAL9SnQy3CySQhVqJzmwRo75VX8ghwVhrhx7kEddmqsvzca-6OV_2dADNoh8uKQtEVBhDQZY9dm9Q76jTwBlWiTFqbUnIuLrUqzbPNA2vpYBFFZukAhu0C2ETvPTUoGzbt3LiXlAldG56-jZnMDp7EkN2Um1GbIS2rEoYRUXCGiR9t8stDky7-3SH6Xpjs4_ljgMgkBZlJHyT_b70dCdueTuT-K26co7dqLAzo5n7sW4fegvJ1RzCICCzhtWjXfUNFqR6im3pHRBA_u1dLBfhS9WEj_swe-L-R9PXgYQUKCuDGL3LzAAwgjj0vvoeVPyR5RQtS8T-NCiSbZRejV6ao08D2Iv6Kr9tZ2Dvs669PyM_HtJ3Rp40Z6C7aWeHU6IKW4Rdvhw1T8Ux0RvncDTVCJOPCwtr5q95xLdTamo5EQgrk9C3HiWaQZ5w3-lNy8pyG-21zJGqGj10zM-HjuOcVM0-cZQO8yqN80cmdS3prbBDTKW3tg-sn-Z44pyM6p8LXiW-zR0JZD_PTZX40eZVkPtYt4aqoKCbub5g4uQ7mnIh4OXF3PQ82T9Pehy',
                'formid':'formquitacaoeleitoral',
                'nome': nome,
                'dataNascimento': data_nascimento,
                'nomeMae': nome_mae,
                'nomePai': nome_pai,
                'cpf': cpf
            }

            headers = {
                "Accept": "application/json; charset=utf-8",
                "Content-Type": "application/json; charset=utf-8"
            }

            console('Enviando requisição...')
            response = requests.post(url, json= body, headers= headers)
            console("response status code: " + str(response.status_code)+"\n\n")

            content = json.loads(response.content)
            console(content['message'])

            if (content['message'] == msg_dados_invalidos or content['message'] == msg_doc_invalido) or content['message'] == msg_recaptcha:
                console("alerta: " + content['message'])
                console("Avaliação deve ser concluida com risco baixo")
                self.abrir_quitacao_eleitoral_para_evidencia_erro(nome, cpf, data_nascimento, nome_mae, nome_pai)
                data['found'] = True
                data['evidence'] = self.take_evidence()
                data['alertas'] = 0
                self.teardown()
            elif (content['status'] == 200):
                console("url: " + content['data']['linkCertidao'])
                self.open_browser(content['data']['linkCertidao'].replace('.pdf', ''))
                self.wait_sleep(5)
                page_text = self.page.query_selector('body').inner_text()
                self.wait_sleep(2)
                data['evidence'] = self.take_evidence()
                data['alertas'] = 0 if page_text.find(textNaoQuite) == -1 else 1
                data['found'] = True
                self.teardown()
            else:
                self.open_browser(url_site)
                raise Exception(content['message'])

            write_results(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            self.teardown()
            raise Exception('Erro: ', e)

    def abrir_quitacao_eleitoral_para_evidencia_erro(self, nome: str, cpf: str, data_nascimento: str, nome_mae: str, nome_pai: str):
        try:
            url = 'https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-quitacao-eleitoral'
            campo_nome_eleitor = '//*[@id="QE_NomeEleitor"]'
            campo_cpf = '//*[@id="QE_NumeroTituloCPF"]'
            campo_data_nascimento = '//*[@id="QE_DataNascimento"]'
            campo_nao_consta_mae = '//*[@id="QE_NaoConstaMae"]'
            campo_nao_consta_pai = '//*[@id="QE_NaoConstaPai"]'
            campo_mae = '//*[@id="QE_NomeMae"]'
            campo_pai = '//*[@id="QE_NomePai"]'
            btn_emitir = '//*[@id="form-quitacao-eleitoral"]/fieldset/button'

            self.open_browser(url)
            self.wait_sleep(3)
            self.input_text(nome, campo_nome_eleitor)
            self.wait_sleep(1)
            self.input_text(cpf, campo_cpf)
            self.wait_sleep(1)
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

            console("Clicando no botão de emitir")
            self.click_at(btn_emitir)
            self.wait_sleep(5)
            self.page.evaluate("document.querySelector('#modal-lgpd').remove()")
            self.wait_sleep(2)
        except:
            raise Exception('Problema na navegação do site.')
