import json, re, base64
from functools import reduce

import robot
from robot.libraries.BuiltIn import BuiltIn

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
from playwright.sync_api import sync_playwright
from robot.api.logger import console

from utils import write_results


@library(scope='GLOBAL', version='0.0.1')
class CoreLib(object):
    '''
    Biblioteca utilizada para escrever os crawlers da ICTS. Esta biblioteca fornece
    palavras chaves que poderão ser utilizadas para escrever scripts do RobotFramework
    para realizar a busca de dados em diversos sites da internet. Caso algum site possua
    alguma estrutura incompatível com esta biblioteca, por favor solicitar o desenvolvimento
    de alguma keyword específica para o site em questão. Abaixo estarão descrita as
    palavras chaves (bem como seu funcionamento e parâmetros) que a biblioteca fornece.
    '''

    @keyword('Abrir o navegador em')
    def open_browser(self, url: str, headless: bool = True, slow_mo: float = None):
        '''
        Inicializa o serviço do playwright, executa o navegador (firefox) e abre uma página na URL especificada.

        Parâmetros:
          - `url`: endereço o qual o navegador deverá acessar
          - `headless`: boleando para configurar se o navegador irá executar em modo headless ou headful
          - `slow_mo`: tempo (em milisegundos) em que o `Playwright` deverá esperar entre suas ações - útil para debug

        Exemplos:
        | Abrir o navegador em | www.google.com |
        | Abrir o navegador em | www.google.com | False |
        | Abrir o navegador em | www.google.com | False | 3000 |
        '''
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(
            headless=headless, slow_mo=slow_mo)
        self.page = self.browser.new_page()
        self.page.goto(url)

    @keyword('Clicar em')
    def click_at(self, selector: str):
        '''
        Clica no elemento que corresponde ao `selector` informado.

        Parâmetros:
        - `selector`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].

        Exemplo:
        | Clicar em | .meu-botao |
        '''
        self.page.click(selector)

    @keyword('Digitar texto em campo')
    def input_text(self, text: str, selector: str):
        '''
        Preenche o `input` que corresponde ao `selector` com o `text` informado

        Parâmetros:
        - `text`: texto a ser preenchido no campo
        - `selector`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].

        Exemplo:
        | Digitar texto em campo | meuemail@gmail.com | \\#email-input |
        '''
        self.page.fill(selector, text)

    @keyword('Esperar até que elemento esteja visivel')
    def wait_for_element(self, selector: str):
        '''
        Espera até que o elemento correspondente ao `selector` esteja visível na página.

        Parâmetros:
        - `selector`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].

        Exemplo:
        | Esperar até que elemento esteja visivel | .minha-tabela |
        '''
        self.page.wait_for_selector(selector)

    @keyword('Pegar dados da tabela em JSON')
    def dump_table(self, selector: str, header_at: int = 1, data_begins_at: int = 2):
        '''
        Realiza o parse da tabela correspondete ao `selector` para JSON e escreve o resultado no arquivo XML de saída do Robot (tag `crawler-result`).

        Parâmetros:
        - `selector`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].
        - `header_at`: em qual linha da tabela o header está presente
        - `data_begins_at`: em qual linha da tabela os dados começam

        Exemplos:
        | Pegar dados da tabela em JSON | .minha-tabela |
        | Pegar dados da tabela em JSON | .minha-tabela | 2 | 4 |
        '''
        table_data: list[dict] = []
        raw_data = self.page.query_selector(selector).inner_text().split('\n')
        headers = raw_data[header_at - 1].split('\t')

        raw_data = raw_data[(data_begins_at - 1):]
        for str_data in raw_data:
            arr_data = str_data.split('\t')
            table_data.append(dict(zip(headers, arr_data)))

        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Extrair resultados CompraSal')
    def extract_comprasal_data(self):
        """"
        Realiza o parse da tabela do CompraSal JSON e escreve o
        resultado no arquivo XML de saída do Robot (tag `crawler-result`).

        Exemplos:
        | Extrair resultados CompraSal |
        """
        table_data: list[dict] = []
        has_more_providers = True
        selector = "#comprasal_1 table tbody tr td:first-child a"
        while has_more_providers:
            self.page.wait_for_selector(selector)
            table_lines = self.page.query_selector_all(selector)
            for table_link in table_lines:
                provider_details = {}
                table_link.click()

                # Provider details
                provider_details_raw = self.page.wait_for_selector('table.ui-panelgrid.ui-widget tbody').inner_text().split(
                    '\n')
                i = 0
                for provider_details_raw_line in provider_details_raw:
                    modal_data_columns = provider_details_raw_line.split('\t')
                    if modal_data_columns[0]:
                        index = modal_data_columns[0].replace(
                            ':', '').replace(' ', '_').lower()
                        provider_details[index] = modal_data_columns[1] if len(
                            modal_data_columns) == 2 else ''
                    i += 1
                    if i == 3:
                        break
                provider_details['sitio_web'] = provider_details_raw[5][0]

                # Provided services
                has_more_services = True
                provided_services = []
                while has_more_services:
                    provided_services.extend(
                        self.page.wait_for_selector('tbody#comprasal_2\\:obsProveedores_data').inner_text().split('\n'))

                    # Services pagination
                    next_services = self.page.query_selector(
                        '#comprasal_2\\:obsProveedores_paginator_bottom a.ui-paginator-next:not(.ui-state-disabled)')
                    if next_services:
                        next_services.click()
                        BuiltIn().sleep('200ms')
                    else:
                        has_more_services = False

                self.page.click('a.ui-dialog-titlebar-close')
                table_data.append({
                    'nombre': table_link.inner_text(),
                    'detalles_del_provedor': provider_details,
                    'bienes_obras_servicos': provided_services
                })

            # Providers pagination
            next_providers = self.page.query_selector(
                '#comprasal_1\\:resultados_paginator_bottom a.ui-paginator-next:not(.ui-state-disabled)')
            if next_providers:
                next_providers.click()
                BuiltIn().sleep('200ms')
            else:
                has_more_providers = False

        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Extrair resultados ComprarArgentina')
    def extract_comprar_argentina_data(self):
        """"
        Realiza o parse da tabela do Comprar Argentina JSON e escreve o
        resultado no arquivo XML de saída do Robot (tag `crawler-result`).

        Exemplos:
        | Extrair resultados Comprar Argentina |
        """
        table_data: list[dict] = []
        has_more_providers = True
        selector = "#ctl00_CPH1_UCBuscarProveedor_gvResultados tr:not(:first-child):not(.pagination-gv) td:first-child a"
        next_page = 2

        while has_more_providers:
            self.page.wait_for_selector(selector)

            for item_index in range(2, 11):
                table_link = self.page.query_selector(
                    "#ctl00_CPH1_UCBuscarProveedor_gvResultados tr:not(:first-child):not(.pagination-gv):nth-child({}) td:first-child a".format(
                        item_index))
                if not table_link:
                    break

                table_link.click()
                self.page.wait_for_selector(
                    '#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_upPanel > div:nth-of-type(2) .col-md-3')

                # Datos del Porvedor
                datos_del_provedor = {}
                provider_info = self.page.query_selector_all(
                    '#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_upPanel > div:nth-of-type(2) .col-md-3')
                for provider_data_raw in provider_info:
                    provider_data = provider_data_raw.inner_text().split('\n\n')
                    index = provider_data[0].replace(' ', '_').lower()
                    datos_del_provedor[index] = provider_data[1] if len(
                        provider_data) == 2 else ''

                # Datos de la persona fisica
                datos_persona_fisica = {}
                persona_fisica_info = self.page.query_selector_all(
                    '#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_divDatosPersonaFisica > .panel-body .col-md-3')
                i = 0
                for persona_fisica_data_raw in persona_fisica_info:
                    persona_fisica_data = persona_fisica_data_raw.inner_text().split('\n\n')
                    index = persona_fisica_data[0].replace(' ', '_').lower()
                    datos_persona_fisica[index] = persona_fisica_data[1] if len(
                        persona_fisica_data) == 2 else ''
                    i = i + 1
                    if i == 8:
                        break

                datos_conjugue = {}
                for persona_fisica_data_raw in persona_fisica_info[8:]:
                    persona_fisica_data = persona_fisica_data_raw.inner_text().split('\n\n')
                    index = persona_fisica_data[0].replace(' ', '_').lower()
                    datos_conjugue[index] = persona_fisica_data[1] if len(
                        persona_fisica_data) == 2 else ''

                # Clases inscriptas
                clases_inscriptas = []
                clases_inscriptas_headers_raw = self.page.query_selector(
                    "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_pnlClasesInscriptas tbody .tr-header")
                if clases_inscriptas_headers_raw:
                    clases_inscriptas_headers_raw = clases_inscriptas_headers_raw.inner_text().split('\t')
                    clases_inscriptas_headers = list(
                        map(lambda header: header.lower().replace(' ', '_'), clases_inscriptas_headers_raw))

                    clases_inscriptas_raw = self.page.query_selector_all(
                        "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_pnlClasesInscriptas tbody tr:not(.tr-header)")
                    for clase_inscripta_raw in clases_inscriptas_raw:
                        clases_inscriptas_info = clase_inscripta_raw.inner_text().replace('\n',
                                                                                          '').split('\t')
                        clases_inscriptas.append(
                            dict(zip(clases_inscriptas_headers, clases_inscriptas_info)))

                # Representante Legal / Apoderado
                representantes_legal = []
                representante_legal_headers_raw = self.page.query_selector(
                    "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_gvAdministradoresLegitimados tbody .tr-header")
                if representante_legal_headers_raw:
                    representante_legal_headers_raw = representante_legal_headers_raw.inner_text().split('\t')
                    representante_legal_headers = list(
                        map(lambda header: header.lower().replace(' ', '_'), representante_legal_headers_raw))

                    representantes_legal_raw = self.page.query_selector_all(
                        "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_gvAdministradoresLegitimados tbody tr:not(.tr-header)")
                    for representante_legal_raw in representantes_legal_raw:
                        representante_legal_info = representante_legal_raw.inner_text().replace('\n',
                                                                                                '').split('\t')
                        representantes_legal.append(
                            dict(zip(representante_legal_headers, representante_legal_info)))

                # Estado de la documentación
                estado_documentacion = []
                estado_documentacion_headers_raw = self.page.query_selector(
                    "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_gvDocumentos tbody .tr-header")
                if estado_documentacion_headers_raw:
                    estado_documentacion_headers_raw = estado_documentacion_headers_raw.inner_text().split('\t')
                    estado_documentacion_legal_headers = list(
                        map(lambda header: header.lower().replace(' ', '_'), estado_documentacion_headers_raw))

                    estado_documentacion_raw = self.page.query_selector_all(
                        "#ctl00_CPH1_UCVerCertificadoEstadoRegistralCiudadano_gvDocumentos tbody tr:not(.tr-header)")
                    for estado_documentacion_raw_item in estado_documentacion_raw:
                        estado_documentacion_info = estado_documentacion_raw_item.inner_text().replace('\n',
                                                                                                  '').split('\t')
                        estado_documentacion.append(
                            dict(zip(estado_documentacion_legal_headers, estado_documentacion_info)))

                table_data.append({
                    'datos_del_proveedor': datos_del_provedor,
                    'datos_de_la_persona_fisica': datos_persona_fisica,
                    'datos_conjugue': datos_conjugue,
                    'classes_inscriptas': clases_inscriptas,
                    'representante_legal': representantes_legal,
                    'estado_de_la_documentacion': estado_documentacion
                })

                self.page.go_back()

            next_providers = self.page.query_selector(
                ".pagination-gv tr td a[href=\"javascript:__doPostBack('ctl00$CPH1$UCBuscarProveedor$gvResultados','Page${}')\"]".format(
                    next_page))
            if next_providers:
                next_providers.click()
                BuiltIn().sleep('1500ms')
                next_page += 1
            else:
                has_more_providers = False

        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Esperar até que elemento não esteja visivel')
    def wait_for_element_hidden(self, selector: str):
        self.page.wait_for_selector(selector, state='hidden')

    @keyword('Esperar')
    def wait_sleep(self, time: str):
        BuiltIn().sleep(time)

    @keyword('Pegar dados da tabela em Hacienda MX JSON passando o seletor do header')
    def dump_table_with_header(self, header: str, data: str):
        '''
            Realiza o parse da tabela correspondete ao `selector` para JSON e escreve o resultado no arquivo XML de saída do Robot (tag `crawler-result`).

            Parâmetros:
            - `header`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].
            - `data`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].

            Exemplos:
            | Pegar dados da tabela em JSON | .minha-tabela |
            | Pegar dados da tabela em JSON | .minha-tabela |
            '''
        table_data: list[dict] = []
        # BuiltIn().sleep('3000ms')
        raw_header = self.page.query_selector(
            header).inner_text().split('\n')
        headers = list(filter(lambda x: x != str('\t'), raw_header))

        raw_data = self.page.query_selector(data).inner_text().split('\n')
        data_values = list(
            filter(lambda x: (x != str('\t') and x != ''), raw_data))
        next_page_btn = self.page.query_selector(
            '#formTabla\:tabla_paginator_top > span.ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)')
        while next_page_btn:
            next_page_btn.click()

            next_page_btn = self.page.query_selector(
                '#formTabla\:tabla_paginator_bottom > span.ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)')
            raw_data_loop = self.page.query_selector(
                data).inner_text().split('\n')
            data_values_loop = list(
                filter(lambda x: (x != str('\t') and x != ''), raw_data_loop))
            data_values.extend(data_values_loop)

        while len(data_values) >= len(headers):
            arr_data = data_values[:len(headers)]
            data_values = data_values[len(headers):]
            table_data.append(dict(zip(headers, arr_data)))
        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Fechar navegador e parar playwright')
    def teardown(self):
        '''
            Utilizado para fechar o navegador e parar o serviço do playwright. É recomendado
            sempre utilizar essa palavra chave no `Teardown` das tarefas para que sempre seja
            executada ao final da tarefa (em caso de sucesso ou falha), dessa forma não deixando
            o serviço do playwright rodando mesmo após a tarefa terminar. Caso o serviço do playwright
            continue executando mesmo após a terefa terminar pode ocasionar problemas nas próximas tarefas.
            '''
        self.page.close()
        self.browser.close()
        self.playwright.stop()

    @keyword('Pegar dados da página perfilProv')
    def pegar_dados_perfilprov(self):
        data = {}
        self.wait_for_element('//*[@id="idPanelA2"]/div[2]/div/app-tile/a/div')

        # Tem contrato?
        card = self.page.query_selector('//*[@id="idPanelA2"]/div[2]/div/app-tile/a/div')
        no_contract = card.query_selector('span.tile__contract-no')
        data['has_contract'] = True if no_contract is None else False

        card.click()
        self.click_at('//html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[3]/span[1]')

        # Pega os dados cadastrais
        profile_content = self.page.query_selector('div.profile-content')
        profile_content_as_list = list(map(lambda x: re.sub(r"\(\*+\)", '', x), filter(lambda x: x != ':', profile_content.inner_text().split('\n'))))
        data['registration'] = { profile_content_as_list[i]: profile_content_as_list[i + 1] for i in range(0, len(profile_content_as_list), 2) }
        data['registration']['Nombre'] = self.page.query_selector('.supplier-card .header .page__title').inner_text()

        # Pega os antecedentes
        right_content_legend = list(map(lambda x: re.sub(r"\n", ' ', x.inner_text()), self.page.query_selector_all('.right-container .score-data .score-legend')))
        right_content_value = list(map(lambda x: x.inner_text(), self.page.query_selector_all('.right-container .score-data .score-value')))
        data['record'] = dict(zip(right_content_legend, right_content_value))

        # Pegar dados societários
        partners_content = self.page.query_selector_all('.data-container .row:nth-child(2) .col-12:first-child .left-spaced')

        try:
            partners_content = list(filter(lambda x: x.query_selector('.contract-title').inner_text() == 'Socios/Accionistas', partners_content))[0]
            partners_content = map(lambda x: x.inner_text().split('\nTipo de Documento: '), partners_content.query_selector_all('.contract-details'))
        except:
            partners_content = []

        def partners_reducer (acc: list, curr):
            acc.append({
                'nombre': curr[0],
                'doc': curr[1]
            })
            return acc

        data['partners'] = reduce(partners_reducer, partners_content, [])

        # Pegar a evidencia
        evidence_bytes = self.page.screenshot(full_page=True)
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(evidence_bytes).decode('utf-8'))
        data['evidence'] = 'data:image/png;base64,{}'.format(evidence_b64)

        write_results(json.dumps(data, ensure_ascii=False))
