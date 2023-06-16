from robot.api.deco import keyword, library
from robot.api.logger import console
from utils import write_results
import json
import NewCoreLib

@library(scope='GLOBAL', version='0.0.1')
class OffShore(NewCoreLib.NewCoreLib):
    @keyword('offshore')
    def main(self, nome: str):
        url_site = 'https://offshoreleaks.icij.org'
        field_search = '//html/body/div[3]/div[1]/div/form/input[1]'
        btn_search = '//html/body/div[3]/div[1]/div/form/div/button'
        checkbox_terms = '//*[@id="accept"]'
        tbody = '#search_results > div.table-responsive > table > tbody tr'
        registered_in = 'body > div.container.node > div > div.node__content.col-lg-8.col-sm-12 > div.node__content__metadata.mb-4.pb-4.pt-4.border-bottom.border-light > div > div > div.col > ul > li:nth-child(1) > div.metadata__properties__row__attribute-value > a'
        agent = 'body > div.container.node > div > div.node__content.col-lg-8.col-sm-12 > div.node__content__metadata.mb-4.pb-4.pt-4.border-bottom.border-light > div > div > div.col > ul > li:nth-child(3) > div.metadata__properties__row__attribute-value'
        incorporated = 'body > div.container.node > div > div.node__content.col-lg-8.col-sm-12 > div.node__content__metadata.mb-4.pb-4.pt-4.border-bottom.border-light > div > div > div.col-lg-5.col-md-5.col-sm-12 > div.metadata__dates.p-3 > div:nth-child(1) > ul > li > div.col-md-10.col-sm-12 > div.metadata__dates__date-value.text-uppercase'
        no_results = '#search_results > p'

        try:
            self.open_browser(url_site)
            self.wait_sleep(2)
            console("Validando se existe modal de aceite dos termos")
            if self.page.query_selector(checkbox_terms) != None:
                self.click_at(checkbox_terms)
                self.wait_sleep(1)
                self.click_at('//*[@id="__BVID__44___BV_modal_body_"]/form/div/div[2]/button')
            self.wait_sleep(3)
            self.input_text('"' + nome + '"', field_search)
            self.wait_sleep(1)
            self.click_at(btn_search)
            self.wait_sleep(5)

            console("Verificando se veio a tabela de resultados")
            table_results = self.page.query_selector_all(tbody)
            if table_results:
                found = True
                read_lines = 1
                results = []
                result_key = 1
                console('Percorrendo tabela de resultados')
                for row in table_results:
                    if read_lines <= 20:
                        row_result = {}
                        row_result['entity'] = row.query_selector('td:nth-child(1)').inner_text()
                        row_result['jurisdiction'] = row.query_selector('td:nth-child(2)').inner_text()
                        row_result['linked_countries'] = 'Dado não encontrado' if row.query_selector('td:nth-child(2)').inner_text() == '' else row.query_selector('td:nth-child(2)').inner_text()
                        row_result['data_from'] = row.query_selector('td:nth-child(4)').inner_text()
                        row_result['entity_details_url'] = row.query_selector('td:nth-child(1) a').get_attribute('href')
                        results.append(row_result)
                        console("Dados inseridos")
                        result_key += 1
                        self.wait_sleep(2)
                    else:
                       console("Lido o limite estabelecido de resultados")
                       break
                    read_lines += 1
                alerts = read_lines - 1

                console("Encerrando navegador para a chamada principal")
                self.teardown()
                self.wait_sleep(2)

                console("Buscando detalhes das entidades encontradas")
                for result in results:
                    console("Abrindo novo site de pesquisa")
                    self.open_browser(url_site+result['entity_details_url'])
                    self.wait_sleep(2)
                    console("Validando se existe modal de aceite dos termos")
                    if self.page.query_selector(checkbox_terms) != None:
                        self.click_at(checkbox_terms)
                        self.click_at('//*[@id="__BVID__55___BV_modal_body_"]/form/div/div[2]/button')
                    self.wait_sleep(2)
                    result['registered_id'] = self.page.query_selector(registered_in).inner_text() if self.page.query_selector(registered_in) != None else 'Dado não encontrado'
                    result['agent'] = self.page.query_selector(agent).inner_text() if self.page.query_selector(agent) != None else 'Dado não encontrado'
                    result['incorporated'] = self.page.query_selector(incorporated).inner_text() if self.page.query_selector(incorporated) != None else 'Dado não encontrado'
                    self.teardown()
                    self.wait_sleep(2)
            elif self.page.query_selector(no_results) != None and self.page.query_selector(no_results).inner_text() == 'No results found':
                found = False
                alerts = 0
                results = False
                self.teardown()
            else:
                raise Exception('Erro fora esperado')

            self.data['results'] = results
            self.data['found'] = found
            self.data['alerts'] = alerts
            write_results(json.dumps(self.data, ensure_ascii=False))
        except Exception as e:
            self.teardown()
            raise Exception('Erro: ', e)




