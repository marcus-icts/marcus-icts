from curses import window
import json, re, base64
from functools import reduce
import os
import robot
from robot.libraries.BuiltIn import BuiltIn

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
from playwright.sync_api import sync_playwright
from robot.api.logger import console
from utils import write_results
from dataUriCaptcha import dataUriCaptcha
from core.env import env
from anticaptchaofficial.recaptchav2proxyless import *
import re
import requests

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
    def open_browser(self, url: str, headless: bool = True, slow_mo: float = None, navegador: str = 'firefox'):
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
        self.browser = self.playwright[navegador].launch(
            headless=headless, slow_mo=slow_mo)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(url, timeout=180000)
        self.data = {}

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
        | Digitar texto em campo | meuemail@gmail.com | #email-input |
        '''
        self.page.fill(selector, text)

    @keyword('Digitar texto em campo nome comprasal')
    def input_text_comprasal(self, text: str):
        '''
        Preenche o `input` que corresponde ao `selector` com o `text` informado
        Parâmetros:
        - `text`: texto a ser preenchido no campo

        Exemplo:
        | Digitar texto em campo | meuemail@gmail.com |
        '''
        self.page.fill("body > app-root > div.min-vh-100.mb-2.container > app-providers > div:nth-child(2) > div > div > div:nth-child(1) > div > input", text)

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
        table_data: dict = {'data':[]}
        raw_data = self.page.query_selector(selector).inner_text().split('\n')
        headers = raw_data[header_at - 1].split('\t')

        raw_data = raw_data[(data_begins_at - 1):]
        for str_data in raw_data:
            arr_data = str_data.split('\t')
            table_data['data'].append(dict(zip(headers, arr_data)))

        table_data['evidence'] = self.take_evidence()


        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Pegar dados mexico em JSON')
    def mexico_table(self, selector: str):
        '''
        Realiza o parse da tabela correspondete ao `selector` para JSON e escreve o resultado no arquivo XML de saída do Robot (tag `crawler-result`).

        Parâmetros:
        - `selector`: seletor css ou xpath do elemento. Para saber mais verificar a [https://playwright.dev/docs/core-concepts#selectors|documentação oficial do playwright sobre seletores].

        Exemplos:
        | Pegar dados da tabela em JSON | .minha-tabela |
        | Pegar dados da tabela em JSON | .minha-tabela | 2 | 4 |
        '''
        table_data: dict = {'data': []}
        raw_data = self.page.query_selector(selector).inner_text().split('\n')
        tempheaders = raw_data[9:29]
        headers = [str for str in tempheaders if str != '\t']
        results = raw_data[29:]
        for result in results:
            result_arr = result.split('\t')
            table_data['data'].append(dict(zip(headers, result_arr)))
        table_data['evidence'] = self.take_evidence()
        write_results(json.dumps(table_data, ensure_ascii=False))

    @keyword('Printar tela')
    def take_evidence(self):
        evidence_bytes = self.page.screenshot(full_page=True)
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(evidence_bytes).decode('utf-8'))

        return 'data:image/png;base64,{}'.format(evidence_b64)


    @keyword('Extrair resultados CompraSal')
    def extract_comprasal_data(self):
        """"
        Realiza o parse da tabela do CompraSal JSON e escreve o
        resultado no arquivo XML de saída do Robot (tag `crawler-result`).

        Exemplos:
        | Extrair resultados CompraSal |
        """
        table_data: dict = {"data": []}
        selector = "body > app-root > div.min-vh-100.mb-2.container > app-providers > div:nth-child(3) > div > div > app-provider-list > div.card.rounded-0.shadow.p-0 > ul > li"
        self.page.wait_for_selector(selector)
        table_lines = self.page.query_selector_all(selector)
        # console(table_lines)
        origin = self.page.evaluate('window.location.origin')
        urls = []
        for line in table_lines:
            urls.append(origin +line.query_selector('app-provider-item > a').get_attribute('href'))
        # console(urls)
        for url in  urls:
            self.page.goto(url, timeout=180000)
            provider_details = {}
            # Provider details
            provider_details = self.page.wait_for_selector(
                'body > app-root > div.min-vh-100.mb-2.container > app-provider-detail'
            ).inner_text().split('\n')
            # console(provider_details)

            tempDetails = provider_details[5:20]
            tempDetails = [str for str in tempDetails if str != '']

            index = 0
            headers = []
            data = []
            for str in tempDetails:
                if (self.check_is_odd(number=index)):
                    data.append(str)
                else:
                    headers.append(str)
                index += 1

            tempAssets = provider_details[23:]

            assets = {}

            if tempAssets:
                tempAssets = [str for str in tempAssets if str != '']
                idx = 0
                assetHeaders = []
                assetData = []
                for str in tempAssets:
                    if (self.check_is_odd(number=idx)):
                        assetData.append(str)
                    else:
                        assetHeaders.append(str)
                    idx += 1

                assets = dict(zip(assetHeaders, assetData))

            table_data['data'].append({
                'nombre': provider_details[0],
                'comercial': provider_details[2],
                'detalles_del_provedor': dict(zip(headers, data)),
                'bienes_obras_servicos': assets,
                'evidence': self.take_evidence()
            })

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
    @keyword('Resolver Captcha')
    def resolve_captcha(self,retry:int = 0):
        self.data = {
            'found': True
        }
        self.wait_for_element('//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaImage"]')
        card = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaImage"]')
        console(len(self.context.pages))
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        # solver.set_key("27d819d5ee02a13d4152ab123f16cd6d")
        solver.set_key(env('CAPTCHA_KEY'))
        # solver.
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))

        if captcha_text != 0:
            print("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            self.page.fill('//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaTextBox"]', captcha_text)
            self.page.click('//*[@id="MasterGC_ContentBlockHolder_cmndNuevaBusquedaNombre"]')
            try:
                error = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblError1"]')
                checkError = error != None
                if not checkError:
                    self.wait_for_element('//*[@id="MasterGC_ContentBlockHolder_gvResultado"]')
                    console('verificando se encontrou resultado')
                    console('encontrou resultado')
                    self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_gvResultado_ctl02_HyperLink1"]').click()
                    self.wait_for_element('//*[@id="MasterGC_ContentBlockHolder_lblNombreProv"]')
                else:
                    console('não encontrou resultado')
                    self.data['found'] = False
            except Exception as e:
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                console(str(e))
                if retry < 3:
                    self.resolve_captcha(retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    self.data['found'] = False
                    self.data['error'] = '4 Tentativas de resolver captcha e não conseguiu, pode ser por tempo ou texto errado'
                    write_results(json.dumps(self.data, ensure_ascii=False))
        else:
            self.data['found'] = False
            self.data['captchaError'] = solver.error_code
            write_results(json.dumps(self.data, ensure_ascii=False))
            print("task finished with error "+solver.error_code)
    @keyword('Dados Cadastrais e societários latam')
    def extract_cadastral_data_latam(self):
        ####### DADOS CADASTRAIS ###################
        if self.data['found'] == True:
            self.wait_for_element('//*[@id="MasterGC_ContentBlockHolder_lblNombreProv"]')
            self.data['cui'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblCUI"]').inner_text()
            self.data['nombre'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblNombreProv"]').inner_text()
            self.data['tipo_organizacion'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblTipoOrganizacion"]').inner_text()
            self.data['nit'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblNIT"]').inner_text()
            if self.page.query_selector('#contenido > div:nth-child(4) > div.cuadroResumen > div > div:nth-child(6) > div.col-xs-12.col-sm-12.col-md-3.col-lg-3 > span').inner_text() == 'Nombre comercial 1:':
                console('tem nome comercial')
                self.data['nombre_comercial'] = self.page.query_selector('#contenido > div:nth-child(4) > div.cuadroResumen > div > div:nth-child(6) > div.col-xs-12.col-sm-12.col-md-9.col-lg-9 > div').inner_text()
            else:
                console('não tem nome comercial')
                self.data['nombre_comercial'] = None
            console(self.page.query_selector('//*[@id="DivDatosAdicionales-tab"]'))
            datosAdicionales = self.page.query_selector('//*[@id="DivDatosAdicionales-tab"]')
            datosAdicionalesCheck = datosAdicionales != None
            if datosAdicionalesCheck:
                console('tem dados adicionais')
                self.data['fecha_de_constitucion'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblFechaConstitucion"]').inner_text()
                self.data['actividad_economica'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblActividadEconomica"]').inner_text()
            else:
                console('não tem dados adicionais')
                self.data['fecha_de_constitucion'] = None
                self.data['actividad_economica'] = None
            datosDomicilioComercial =  self.page.query_selector('//*[@id="DivDomicilioComercial-tab"]')
            datosDomicilioComercialCheck = datosDomicilioComercial != None
            if datosDomicilioComercialCheck:
                console('tem dados domicilio comercial')
                self.page.query_selector('//*[@id="DivDomicilioComercial-tab"]').click()
                console(self.page.query_selector('#MasterGC_ContentBlockHolder_lblComPagina').inner_text())
                if self.page.query_selector('#MasterGC_ContentBlockHolder_lblComPagina').inner_text():
                    self.data['pagina_web'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblComPagina').inner_text()
                else:
                    self.data['pagina_web'] = None
                if self.page.query_selector('#MasterGC_ContentBlockHolder_lblComCorreo').inner_text():
                    self.data['correo_electronico'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblComCorreo').inner_text()
                else:
                    self.data['correo_electronico'] = None
                if self.page.query_selector('#MasterGC_ContentBlockHolder_lblComDireccion').inner_text():
                    self.data['endereco'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblComDireccion').inner_text()
                else:
                    self.data['endereco'] = None
                if self.page.query_selector('#MasterGC_ContentBlockHolder_lblComTelefono').inner_text():
                    self.data['telefone'] = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblComTelefono"]').inner_text()
                else:
                    self.data['telefone'] = None
            else:
                console('não tem dados domicilio comercial')
                self.data['pagina_web'] = None
                self.data['correo_electronico'] = None
                self.data['endereco'] = None
                self.data['telefone'] = None
            datosRepresentante = self.page.query_selector('#DivRepresentante-tab')
            datosRepresentanteCheck = datosRepresentante != None
            if datosRepresentanteCheck:
                self.page.query_selector('#DivRepresentante-tab').click()
            datoskey = 0
            self.data['representantes'] = []
            ####### PEGANDO REPRESENTANTES ##############
            ####### DADOS SOCIETÁRIOS ###################
            while True:
                info = None
                try:
                    info = self.page.query_selector_all('#MasterGC_ContentBlockHolder_gvRepresentantesLegales > tbody > .FilaTablaDetalle')[datoskey]
                except:
                    break
                datoskey += 1
                datos = {}
                datos['representante'] = info.query_selector('td:nth-child(1)').inner_text()
                datos['proveedor'] = info.query_selector('td:nth-child(2)').inner_text()
                datos['plazo'] = info.query_selector('td:nth-child(3)').inner_text()
                values = info.query_selector('td:nth-child(4) > input')
                subdatos = {}
                if values:
                    info.query_selector('td:nth-child(4) > input').click()
                    self.page.wait_for_selector('.close[data-dismiss=modal]')
                    subinfos = self.page.query_selector_all('#MasterGC_ContentBlockHolder_wuDetalleRepresentados_gdvDetalleRep > tbody > .FilaTablaDetalle')
                    for subinfo in subinfos:
                        key = subinfo.query_selector('td:nth-child(1)').inner_text()
                        subdatos[key] = subinfo.query_selector('td:nth-child(2)').inner_text()
                    self.page.query_selector('.close[data-dismiss=modal]').click()
                datos['subrepresentes'] = subdatos
                self.data['representantes'].append(datos)

    @keyword('Tema Reputacional')
    def extract_data_reputacional(self):
    ######### PEGANDO INCONFORMIDADES ###########
    ######### TEMA REPUTACIONAL #################
        inconformidades = self.page.query_selector('#Inconformidades-tab')
        inconformidadesCheck = inconformidades != None
        counter = 0
        # console('pegando a url')
        # console(self.page.url)
        self.data['url'] = self.page.url
        if inconformidadesCheck:
            inconformidades.click()
            inconformidadesInfos = self.page.query_selector_all('#MasterGC_ContentBlockHolder_gvInconformidades > tbody > tr.FilaTablaDetalle')
            for inconformidade in inconformidadesInfos:
                if inconformidade.query_selector('span.TablaItemAzulSm').inner_text() == 'Aceptada':
                    counter += 1
        self.data['inconformidades_aceitas'] = counter
        # Pegar a evidencia
        evidence_bytes = self.page.screenshot(full_page=True)
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(evidence_bytes).decode('utf-8'))
        self.data['evidence'] = 'data:image/png;base64,{}'.format(evidence_b64)
        write_results(json.dumps(self.data, ensure_ascii=False))
    @keyword('Tema Financeiro')
    def extract_latam_financial_data(self):
        ######### PEGANDO VALOR MONETÁRIO ###########
        ######### TEMA FINANCEIRO &&#################
        # console('pegando a url')
        # console(self.page.url)
        self.data['url'] = self.page.url
        # Pegar a evidencia
        evidence_bytes = self.page.screenshot(full_page=True)
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(evidence_bytes).decode('utf-8'))
        self.data['evidence'] = 'data:image/png;base64,{}'.format(evidence_b64)
        if self.page.query_selector('#NOGS-tab'):
            self.page.query_selector('#NOGS-tab').click()
        money = self.page.query_selector('#MasterGC_ContentBlockHolder_dbResumen > tbody > tr.FooterTablaDetalle')
        if money:
            moneyValue = money.query_selector('td:nth-child(7)').inner_text()
            console("Pegando o valor já recebido")
            console("tratando valor recebido")
            console("Armazenando valor tratado")
            self.data['valor_recebido'] = moneyValue
            self.page.goto('https://www.xe.com/currencyconverter/convert/?Amount='+moneyValue+'&From=GTQ&To=USD', 180000)
            # self.page.wait_for_selector('#__next > div:nth-child(2) > div.fluid-container__BaseFluidContainer-qoidzu-0.gJBOzk > section > div:nth-child(2) > div > main > form > div:nth-child(2) > div:nth-child(1) > p.result__BigRate-sc-1bsijpp-1.iGrAod')
            moneyTransformed = self.page.query_selector('#__next > div:nth-child(2) > div.fluid-container__BaseFluidContainer-qoidzu-0.gJBOzk > section > div:nth-child(2) > div > main > form > div:nth-child(2) > div:nth-child(1) > p.result__BigRate-sc-1bsijpp-1.iGrAod').inner_text()
            console(moneyValue)
            console(moneyTransformed)
            console("Pegando valor em dolar")
            self.data['valor_usd'] = moneyTransformed
            console(self.data)
        else:
            console("Não pega o valor já recebido pois não contém")
            self.data['valor_recebido'] = None
        write_results(json.dumps(self.data, ensure_ascii=False))
    @keyword('Tema Corrupcao')
    def extract_latam_corrupcao_data(self):
        ###### VERIFICANDO SE TEM INABILITADOS #####
        ######### PEGANDO INABILITADOS ##############
        ######### TEMA CORRUPCAO ####################
        inabilitados = self.page.query_selector('#Inhabilitaciones-tab')
        checkInabilitadosTeste = inabilitados != None
        checkInabilitados= False
        if checkInabilitadosTeste:
            console('verificando se tem esse texto')
            if inabilitados.inner_text() == 'Inhabilitaciones':
                checkInabilitados = True
                inabilitados.click()
                self.data['inabilitados'] = []
                if checkInabilitados:
                    ######### PEGANDO INABILITADOS ##############
                    self.page.goto('https://www.guatecompras.gt/inhabilitaciones/consultaProveeInhabRes.aspx', 180000)
                    provedoresInabilitadosKey = 0
                    while True:
                        provedor = None
                        try:
                            provedor = self.page.query_selector_all('#MasterGC_ContentBlockHolder_dbResumen > tbody > tr.FilaTablaDetalle')[provedoresInabilitadosKey]
                        except:
                            break
                        checkProvedor = str(provedor.query_selector("td:nth-child(3) > a").inner_text()) != '0'
                        if checkProvedor:
                            provedor.query_selector("td:nth-child(3) > a").click()
                            provedoresKey = 0
                            while True:
                                provedorInfo = None
                                try:
                                    provedorInfo = self.page.query_selector_all('#MasterGC_ContentBlockHolder_dgResultado > tbody > tr.FilaTablaDetalle')[provedoresKey]
                                except:
                                    break
                                provedorInfoCheck = provedorInfo.query_selector('td:nth-child(1)').inner_text() == self.data['nombre']
                                if provedorInfoCheck:
                                    provedorInfo.query_selector('td:nth-child(2) > a').click()
                                    evidenciaKey = 0
                                    while True:
                                        evidenciaInfo = None
                                        try:
                                            evidenciaInfo = self.page.query_selector_all('#MasterGC_ContentBlockHolder_dgResultado > tbody > tr.FilaTablaDetalle')[evidenciaKey]
                                        except:
                                            break
                                        evidenciaInfo.query_selector('td:nth-child(4) > a').click()
                                        dadosInabilitados = {}
                                        self.page.wait_for_selector('#MasterGC_ContentBlockHolder_lblMotivo')
                                        dadosInabilitados['motivo'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblMotivo').inner_text()
                                        dadosInabilitados['o_que_provocou'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblHecho').inner_text()
                                        dadosInabilitados['duracao'] =self.page.query_selector('#MasterGC_ContentBlockHolder_lblDuracion').inner_text()
                                        dadosInabilitados['inicio'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblFechaCreacion').inner_text()
                                        dadosInabilitados['termino'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblFechaVencimiento').inner_text()
                                        dadosInabilitados['status'] = self.page.query_selector('#MasterGC_ContentBlockHolder_lblEstatus').inner_text()
                                        self.data['inabilitados'].append(dadosInabilitados)
                                        evidenciaKey = evidenciaKey + 1
                                        self.page.go_back()
                                    self.page.go_back()
                                else:
                                    console('indo para o próximo')
                                provedoresKey = provedoresKey + 1
                            self.page.go_back()
                        else:
                            console("passando para o próximo")
                        provedoresInabilitadosKey = provedoresInabilitadosKey + 1
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Pegar dados da página perfilProv')
    def pegar_dados_perfilprov(self):
        data = {
            'found': True
        }

        try:
            self.wait_for_element('//*[@id="idPanelA2"]/div[2]/div/app-tile/a/div')
        except:
            data['found'] = False
            write_results(json.dumps(data, ensure_ascii=False))
            return


        # Tem contrato?
        card = self.page.query_selector('//*[@id="idPanelA2"]/div[2]/div/app-tile/a/div')
        no_contract = card.query_selector('span.tile__contract-no')
        data['has_contract'] = True if no_contract is None else False

        card.click()
        self.click_at('//html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[2]/div/div[3]/span[1]')
        # Pega os dados cadastrais

        data['registration'] = {
            'Nombre': self.page.query_selector('.supplier-card .header .page__title').inner_text()
        }

        profile_content = self.page.query_selector('div.profile-content')

        infos = profile_content.query_selector_all('.info')
        for info in infos:
            key = re.sub(r"\(\*+\)", '', info.query_selector('.info-label').inner_text())
            values = info.query_selector_all('.info-value')

            if len(values) == 0:
                email_values = info.query_selector_all('.emails-list a')
                if len(email_values) == 0:
                    data['registration'][key] = '-'
                else:
                    data['registration'][key] = list(map(lambda x: x.inner_text(), email_values))
            elif len(values) == 1:
                data['registration'][key] = values[0].inner_text()
            else:
                data['registration'][key] = list(map(lambda x: x.inner_text(), values))

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
        data['evidence'] = self.take_evidence()

        write_results(json.dumps(data, ensure_ascii=False))

    @keyword('Resolver QsaCaptcha')
    def resolver_qsacaptcha(self, cnpj: str):
        console('Resolvendo QsaCaptcha')
        self.data = {
            'found': True
        }
        key = 1
        retry = 0
        self.wait_for_element('#captchaSonoro')
        self.page.query_selector('#captchaSonoro').click()
        self.wait_for_element('#imgCaptcha')
        card = self.page.query_selector('#imgCaptcha')
        console(len(self.context.pages))
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))

        if captcha_text != 0:
            console("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            self.page.fill('#txtTexto_captcha_serpro_gov_br', captcha_text)
            self.page.query_selector('#frmConsulta > div:nth-child(4) > div > button.btn.btn-primary').click()
            dadosCadastrais = {}
            qsaData = {}
            try:
                console('tentando pegar o resultado')
                self.page.query_selector('//*[@id="cnpj"]').click()
                self.page.fill('//*[@id="cnpj"]',re.sub('/\d/','',cnpj))
                self.page.click('//*[@id="frmConsulta"]/div[3]/div/button[1]')
                dados = {}
                BuiltIn().sleep('3')
                paginas = self.page.query_selector('//*[@id="principal"]/table[2]/tbody/tr/td[2]/p/font/b').inner_text()
                numeroDePaginas = paginas.split('/')
                console('Número de páginas: ' + numeroDePaginas[1])
                qtdPaginaTotal = int(numeroDePaginas[1])
                paginaAtual = 1
                registro = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[2]/tbody/tr/td[1]/font[2]/b[1]').inner_text()
                dadosCadastrais['cnpj'] = registro
                console('Registro: ' + registro)
                dataAbertura = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[2]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['dataAbertura'] = dataAbertura
                console('Data da Abertura ' + dataAbertura)
                razaoSocial = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[3]/tbody/tr/td/font[2]/b').inner_text()
                dadosCadastrais['razaoSocial'] = razaoSocial
                console('Razão social ' + razaoSocial)
                nomeFantasia = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[4]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['nomeFantasia'] = nomeFantasia
                console('Nome Fantasia ' + nomeFantasia)
                porte = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[4]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['porte'] = porte
                console('Porte ' + porte)
                cnaePrincipal = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[5]/tbody/tr/td/font[2]/b').inner_text()
                dadosCadastrais['cnaePrincipal'] = cnaePrincipal
                console('Cnae Principal ' + cnaePrincipal)
                ##VERIFICANDO SE TEM CNAE SECUNDARIO##
                cnaeSecundario = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[6]/tbody/tr/td/font[2]/b')
                console('verificando se tem esse texto')
                if cnaeSecundario.inner_text() != 'Não informada':
                    console('Tem cnae secundário')
                    infos = self.page.query_selector_all('#principal > table:nth-child(1) > tbody > tr > td > table:nth-child(11) > tbody > tr > td > font')
                    for info in infos:
                        if info.inner_text() != 'CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS':
                            console(info.inner_text())
                            dados[key] = info.inner_text()
                            key += 1
                        else :
                            console('Título de cnae secundario encontrado')
                            console(info.inner_text())
                else :
                    console('Não tem cnae secundario')
                    dadosCadastrais['cnaeSecundario'] = {}
                naturezaJuridica = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[7]/tbody/tr/td/font[2]/b').inner_text()
                dadosCadastrais['naturezaJuridica'] = naturezaJuridica
                console('Natureza Juridica ' + naturezaJuridica)
                logradouro = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[8]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['logradouro'] = logradouro
                console('Logradouro ' + logradouro)
                logradouroNumero = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[8]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['logradouroNumero'] = logradouroNumero
                console('Logradouro Número ' + logradouroNumero)
                logradouroComplemento = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[8]/tbody/tr/td[5]/font[2]/b').inner_text()
                dadosCadastrais['logradouroComplemento'] = logradouroComplemento
                console('Logradouro Complemento ' + logradouroComplemento)
                cep = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[9]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['cep'] = cep
                console('CEP ' + cep)
                bairro = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[9]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['bairro'] = bairro
                console('Bairro ' + bairro)
                municipio = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[9]/tbody/tr/td[5]/font[2]/b').inner_text()
                dadosCadastrais['municipio'] = municipio
                console('Município ' + municipio)
                uf = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[9]/tbody/tr/td[7]/font[2]/b').inner_text()
                dadosCadastrais['uf'] = uf
                console('UF ' + uf)
                email = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[10]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['email'] = email
                console('E-mail ' + email)
                telefone = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[10]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['telefone'] = telefone
                console('Telefone ' + telefone)
                situacaoCadastral = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[12]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['situacaoCadastral'] = situacaoCadastral
                console('Situação Cadastral ' + situacaoCadastral)
                dataSituacaoCadastral = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[12]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['dataSituacaoCadastral'] = dataSituacaoCadastral
                console('Data Situação Cadastral ' + dataSituacaoCadastral)
                motivoSituacaoCadastral = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[13]/tbody/tr/td/font[2]/b').inner_text()
                if motivoSituacaoCadastral == '':
                    dadosCadastrais['motivoSituacaoCadastral'] = 'Não informado'
                else:
                    dadosCadastrais['motivoSituacaoCadastral'] = motivoSituacaoCadastral
                console('Motivo Situação Cadastral ' + motivoSituacaoCadastral)
                situacaoEspecial = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[14]/tbody/tr/td[1]/font[2]/b').inner_text()
                dadosCadastrais['situacaoEspecial'] = situacaoEspecial
                console('Situacao Especial ' + situacaoEspecial)
                dataSituacaoEspecial = self.page.query_selector('//*[@id="principal"]/table[1]/tbody/tr/td/table[14]/tbody/tr/td[3]/font[2]/b').inner_text()
                dadosCadastrais['dataSituacaoEspecial'] = dataSituacaoEspecial
                console('Data Situacao Especial ' + dataSituacaoEspecial)

                #### VERIFICA SE TEM MAIS DE UMA PÁGINA ####
                if paginaAtual != qtdPaginaTotal :
                    index = 1
                    while (paginaAtual < qtdPaginaTotal):
                        paginaAtual += 1
                        tabelaUtilizada = paginaAtual+index
                        console('Número da tabela a ser utilizada' + str(tabelaUtilizada))
                        caminho= '//*[@id="principal"]/table['+str(tabelaUtilizada)+']/tbody/tr/td/table[4]/tbody/tr/td/font'
                        console(caminho)
                        tabelaInfos = self.page.query_selector_all(caminho)
                        for tabelaInfo in tabelaInfos:
                            if tabelaInfo.inner_text() != 'CÓDIGO E DESCRIÇÃO DAS ATIVIDADES ECONÔMICAS SECUNDÁRIAS':
                                console(tabelaInfo.inner_text())
                                dados[key] = tabelaInfo.inner_text()
                                key += 1
                            else :
                                console('Título de cnae secundario encontrado')
                                console(tabelaInfo.inner_text())
                        index += 1
                else :
                    console('Não tem páginas adicionais')
                dadosCadastrais['cnaeSecundario'] = dados
                self.data['dadosCadastrais'] = dadosCadastrais
                self.data['dadosCadastraisEvidencia'] = self.take_evidence()
                validateQsa = self.page.query_selector('.btn-primary')
                if validateQsa :
                    self.page.query_selector('//*[@id="app"]/div/div/div/div/div[3]/div/div/div/button[1]').click()
                    BuiltIn().sleep('3')
                    capitalSocial = self.page.query_selector('//*[@id="capital"]/div[3]/div[2]').inner_text()
                    qsaData['capitalSocial'] = capitalSocial
                    console('Capital Social ' + capitalSocial)
                    qsaInfos = self.page.query_selector_all('#principal > div > div > div')
                    socios = {}
                    sociosKey = 1;
                    for qsa in qsaInfos:
                        linha = {}
                        queryText = qsa.query_selector('.col-md-12 > .alert > div:nth-child(1) > .col-md-9')
                        if queryText != None :
                            linha['socio'] = qsa.query_selector('.col-md-12 > .alert > div:nth-child(1) > .col-md-9').inner_text()
                            linha['cargo'] = qsa.query_selector('.col-md-12 > .alert > div:nth-child(2) > .col-md-5').inner_text()
                            socios[sociosKey] = linha
                            sociosKey += 1
                        else :
                            console('não tem informação desse sócio nessa div')
                    qsaData['socios'] = socios
                    self.data['qsa'] = qsaData
                    self.data['qsaEvidencia'] = self.take_evidence()
                else :
                    self.data['qsaEvidencia'] = self.take_evidence()
                    self.data['qsa'] = {}
                write_results(json.dumps(self.data, ensure_ascii=False))
            except Exception as e:
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                console(str(e))
                if retry < 3:
                    self.resolver_qsacaptcha(retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    self.data['found'] = False
                    self.data['error'] = '4 Tentativas de resolver captcha e não conseguiu, pode ser por tempo ou texto errado'
                    write_results(json.dumps(self.data, ensure_ascii=False))
        else:
            self.data['found'] = False
            self.data['captchaError'] = solver.error_code
            write_results(json.dumps(self.data, ensure_ascii=False))
            print("task finished with error "+solver.error_code)

    @keyword('Resolver captcha imagem FGTS')
    def resolver_captcha_imagem(self,retry: int = 0):
        console('Resolvendo captcha Imagem')
        self.data = {'found': True}
        self.page.wait_for_selector('#captchaImg_N2')
        card = self.page.query_selector('#captchaImg_N2')
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))
        console(captcha_text)
        if captcha_text != 0:
            console("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            # if retry == 0 :
            #     self.page.fill('#mainForm\:txtCaptcha', 'lalala')
            # else :
            self.page.fill('#mainForm\:txtCaptcha', captcha_text)

            self.page.query_selector('//*[@id="mainForm:btnConsultar"]').click()
            try:
                self.page.query_selector('//*[@id="mainForm"]/fieldset[1]/legend/span/h3').inner_text()
            except Exception as e:
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                console(str(e))
                if retry < 3:
                    self.resolver_captcha_imagem(retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    self.data['found'] = False
                    self.data['error'] = '4 Tentativas de resolver captcha e não conseguiu, pode ser por tempo ou texto errado'
                    write_results(json.dumps(self.data, ensure_ascii=False))
        else:
            self.data['found'] = False
            self.data['captchaError'] = solver.error_code
            write_results(json.dumps(self.data, ensure_ascii=False))
            print("task finished with error "+solver.error_code)

    @keyword('Capturar Texto FGTS')
    def capturar_texto(self):
        regular = self.page.query_selector('//*[@id="mainForm"]/div[1]/div/span')
        check_regular = regular != None
        texto = ''
        if check_regular :
            texto = self.page.query_selector('//*[@id="mainForm"]/div[1]/div/span').inner_text()
            self.page.query_selector('//*[@id="mainForm:j_id52"]').click()
            self.page.wait_for_selector('#mainForm > fieldset:nth-child(4) > div > p')
            declaracao = self.page.query_selector('#mainForm > fieldset:nth-child(4) > div > p').inner_text()
            validade = self.page.query_selector('//*[@id="mainForm"]/fieldset[4]/div/p').inner_text()
            certificado = self.page.query_selector('#mainForm > fieldset:nth-child(5) > div > p > span').inner_text()
            data_informacao = self.page.query_selector('#mainForm > div:nth-child(6) > p > span:nth-child(2)').inner_text()
            self.data['declaracao'] = declaracao
            self.data['validade'] = validade
            self.data['certificado'] = certificado
            self.data['data_informacao'] = data_informacao
            self.data['regular'] = True
        else :
            texto = self.page.query_selector('//*[@id="mainForm"]/div[2]/div/span').inner_text()
            self.data['regular'] = False
        self.data['regularidade'] = texto
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Selecionar')
    def selecionar(self, element: str, value: str):
        self.page.select_option(element, value)

    @keyword('Honduras')
    def honduras(self):
        self.data = {
            'found': True
        }
        try:
            self.page.wait_for_selector('//*[@id="ctl00_cphCuerpo_gvProveedores_ctl02_hpObservaciones"]')
            self.page.query_selector('//*[@id="ctl00_cphCuerpo_gvProveedores_ctl02_hpObservaciones"]').click()
            self.data["cnpj"] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[1]/td[2]').inner_text()
            self.data['razao_social'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[2]/td[2]').inner_text()
            self.data['nome_fantasia'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[3]/td[2]').inner_text()
            self.data['categoria'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[4]/td[2]').inner_text()
            self.data['tipo_empresa'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[9]/td[2]').inner_text()
            self.data['inicio'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[11]/td[2]').inner_text()
            self.data['contato'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[13]/td[2]').inner_text()
            self.data['endereco'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_dvProveedor"]/tbody/tr[14]/td[2]').inner_text()
            observacao = self.page.query_selector('//*[@id="ctl00_cphCuerpo_gvObservaciones"]/tbody/tr[2]/td[1]')
            if observacao:
                self.data['observacao'] = self.page.query_selector('//*[@id="ctl00_cphCuerpo_gvObservaciones"]/tbody/tr[2]/td[1]').inner_text()
        except Exception as e:
            self.data['found'] = False
            self.data['error'] = 'Resultado não encontrado'
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Extrair span TCU')
    def extrairTcu(self):
        self.data = {'found': True}
        regular = self.page.query_selector('body > p:nth-child(8) > font > span')
        check_regular = regular != None
        if check_regular :
            console('Caso negativo')
            self.data['span'] = self.page.query_selector('body > p:nth-child(8) > font > span').inner_text()
            self.data['valid_response'] = True
            self.data['alert'] = False
            console('Capturando evidencia')
            self.data['evidence'] =  self.take_evidence()
        else :
            console('Caso positivo')
            self.data['span'] = self.page.query_selector('//*[@id="msgErro"]/tbody').inner_text()
            console(self.data['span'])
            self.data['valid_response'] = True
            self.data['alert'] = True
            self.data['evidence'] =  self.take_evidence()
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Pegar dados da tabela Falencia')
    def get_table_information(self):
        self.data['found'] = True
        ocorrencias = self.page.query_selector_all('//*[@id="gridResultado"]/tbody')
        ocorrencia_geral = {}
        ocorrencia_key = 1
        for ocorrencia in ocorrencias:
            linha = {}
            query_text = ocorrencia.query_selector('td:nth-child(2)')
            if query_text != None :
                linha['razao_social'] = ocorrencia.query_selector('td:nth-child(1)').inner_text()
                linha['cnpj'] = ocorrencia.query_selector('td:nth-child(2)').inner_text()
                linha['ocorrencia'] = ocorrencia.query_selector('td:nth-child(3)').inner_text()
                linha['data'] = ocorrencia.query_selector('td:nth-child(4)').inner_text()
                linha['vara'] = ocorrencia.query_selector('td:nth-child(5)').inner_text()
                linha['fonte'] = ocorrencia.query_selector('td:nth-child(6)').inner_text()
                linha['processo'] = ocorrencia.query_selector('td:nth-child(7)').inner_text()
                ocorrencia_geral[ocorrencia_key] = linha
                ocorrencia_key += 1
                self.data['evidence'] = self.take_evidence()
                self.data['ocorrencias'] = ocorrencia_geral
            else :
                console('Não tem informação de alerta')
        if ocorrencia_key > 1:
            self.data['alertas'] = ocorrencia_key - 1
        else :
            self.data['evidence'] = self.take_evidence()
            self.data['alertas'] = 0
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Resolver captcha imagem')
    def resolver_captcha_imagem(self,selector: str, input: str, click:str, check: str, retry: int = 0):
        console('Resolvendo captcha Imagem')
        self.page.wait_for_selector(selector)
        card = self.page.query_selector(selector)
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))
        console(captcha_text)
        if captcha_text != 0:
            console("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            self.page.fill(input, captcha_text)

            self.page.query_selector(click).click()
            check_true_captcha = self.page.query_selector(check)
            if check_true_captcha == None :
                console('Passou pelo captcha corretamente')
            else :
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                if retry < 3:
                    self.resolver_captcha_imagem(selector, input, click, check, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    self.data['found'] = False
                    self.data['error'] = '4 Tentativas de resolver captcha e não conseguiu, pode ser por tempo ou texto errado'
                    write_results(json.dumps(self.data, ensure_ascii=False))
        else:
            self.data['found'] = False
            self.data['captchaError'] = solver.error_code
            write_results(json.dumps(self.data, ensure_ascii=False))
            print("task finished with error "+solver.error_code)

    @keyword('Resolver captcha imagem bacen')
    def resolver_captcha_imagem_bacen(self,selector: str, input: str, click:str, check: str, retry: int = 0):
        console('Resolvendo captcha Imagem')
        self.page.wait_for_selector(selector)
        card = self.page.query_selector(selector)
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))
        console(captcha_text)
        self.wait_sleep(4)
        if captcha_text != 0:
            console("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            self.page.fill(input, captcha_text)

            self.page.query_selector(click).click()
            self.wait_sleep(4)
            check_true_captcha = self.page.query_selector(check)
            string = ' Não foi possível emitir a certidão automaticamente. Por gentileza, apresente seu pedido de certidão negativa ao Departamento de Resolução e de Ação Sancionadora (Derad), via protocolo digital (https://www.bcb.gov.br/acessoinformacao/protocolodigital). Durante a protocolização, selecione o assunto "Processo Administrativo Sancionador".'
            string_outro_irregular = ' Não foi possível emitir a certidão automaticamente. Por gentileza, apresente seu pedido de certidão negativa via protocolo digital (https://www.bcb.gov.br/acessoinformacao/protocolodigital). Durante a protocolização, selecione o assunto "Outros assuntos", sugerindo se tratar de solicitação de "Certidão Negativa de Administração de Instituição em Liquidação Extrajudicial (Lei Complementar 64/1990, art. 1º, l, i)", a ser direcionado ao Departamento de Resolução e de Ação Sancionadora (Derad).'
            string_irregular = 'O CPF informado não está com a situação regular'
            if check_true_captcha == None:
                console('Passou pelo captcha corretamente')
            elif (
                    (self.page.query_selector(check).inner_text() == string) or
                    (self.page.query_selector(check).inner_text() == string_irregular) or
                    (self.page.query_selector(check).inner_text() == string_outro_irregular)
                ) :
                console('Passou pelo captcha corretamente gerando alerta')
            else :
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                if retry < 3:
                    self.resolver_captcha_imagem_bacen(selector, input, click, check, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    raise Exception('Após 4 tentativas o captcha não foi resolvido')
                write_results(json.dumps(self.data, ensure_ascii=False))
        else:
            self.data['found'] = False
            self.data['captchaError'] = solver.error_code
            write_results(json.dumps(self.data, ensure_ascii=False))
            print("task finished with error "+solver.error_code)

    @keyword('Resolver TCU recaptchaV2')
    def solve_tcu_recaptcha_v2(self, site_url: str, website_key: str):
        self.fill_recaptcha_v2(site_url, website_key)
        console("Validando resposta do captcha...")
        self.page.evaluate(f"window.recaptchaCallback()")
        console(self.page.evaluate(f"window.validaCaptcha()"))

    def fill_recaptcha_v2(self, site_url: str, website_key: str):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        solver.set_website_url(site_url)
        solver.set_website_key(website_key)
        g_response = solver.solve_and_return_solution() #resposta do captcha
        console(g_response)
        if g_response != 0:
            console("Inserindo resposta do captcha no textArea...")
            self.page.eval_on_selector('#g-recaptcha-response', "(el) => el.removeAttribute('style')")
            self.page.fill('#g-recaptcha-response', g_response)

    @keyword('Resolver imagem recaptchaV2')
    def recaptchaV2(self, site_url: str, website_key: str, retry: int = 0):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        solver.set_website_url(site_url)
        solver.set_website_key(website_key)
        g_response = solver.solve_and_return_solution() #resposta do captcha
        if g_response != 0:
            console("Inserindo resposta do captcha no textArea...")
            self.page.eval_on_selector('.grecaptcha-badge', "(el) => el.removeAttribute('style')")
            self.page.eval_on_selector('#g-recaptcha-response', "(el) => el.removeAttribute('style')")

            console("Validando resposta do captcha...")
            self.page.fill('#g-recaptcha-response', g_response)
            self.page.evaluate(f"window.recaptchaV2CallbackSucessoValidacao(['{g_response}'])")

            console('Limpando tela para obter somente a informação necessária...')
            self.page.evaluate('Array.from(document.querySelectorAll("body > div:not(#app, #recaptcha-v2)")).forEach((e) => e.remove())')

            self.wait_sleep(15)
            console('Analisando resultado...')
            selector_cert_negativa = "#app > div > div:nth-child(2) > div > div.folha-a4 > div > div > table > tbody > tr > td > p:nth-child(5) > span"
            elem_cert_negativa = self.page.is_visible(selector_cert_negativa)

            selector_cert_positiva = "#app > div > div:nth-child(2) > form > div > div > div > div.md-card-content > div:nth-child(1) > p:nth-child(1)"
            elem_cert_positiva = self.page.is_visible(selector_cert_positiva)

            selector_cert_positiva_new = '//*[@id="app"]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]' #foi encontrado inicialmente para civel pj
            elem_cert_positiva_new = self.page.is_visible(selector_cert_positiva_new)

            selector_doc_not_found = "body > div.md-dialog > div > div.md-dialog-content.md-theme-default"
            elem_doc_not_found = self.page.is_visible(selector_doc_not_found)

            msg = ''
            if (elem_cert_negativa):
                msg = self.page.inner_text(selector_cert_negativa)
            elif(elem_cert_positiva):
                msg = self.page.inner_text(selector_cert_positiva)
            elif(elem_cert_positiva_new):
                msg = self.page.inner_text(selector_cert_positiva_new)
            elif(elem_doc_not_found):
                msg = self.page.inner_text(selector_doc_not_found)

            console(f'msg: {msg}')

            if (
                msg == 'CERTIFICAMOS, na forma da lei, que, consultando os sistemas processuais abaixo indicados, NÃO CONSTAM, até a presente data, PROCESSOS de classes CÍVEIS em tramitação contra:' or
                msg == 'CERTIFICAMOS, na forma da lei, que, consultando os sistemas processuais abaixo indicados, NÃO CONSTAM, até a presente data e hora, PROCESSOS com com potencial de gerar inelegibilidade contra:' or
                msg == 'CERTIFICAMOS, na forma da lei, que, consultando os sistemas processuais abaixo indicados, NÃO CONSTAM, até a presente data e hora, PROCESSOS de classes CRIMINAIS contra:'
            ):
                console('Passou pelo captcha corretamente')
                self.data['found'] = True
                self.data['evidence'] = self.take_evidence()
                self.data['alertas'] = 0
            elif (msg == 'Essa certidão não pôde ser emitida de forma automática.' or msg == 'Esta certidão não poderá ser requerida pela internet. Será necessário enviar requerimento fundamentado para seipr@jfrj.jus.br (SJRJ) ou naj@jfes.jus.br (SJES).'):
                console('Passou pelo captcha corretamente gerando alerta')
                console('Removendo elemento quebrado..')
                self.page.evaluate("document.querySelector('#app > div > div.md-toolbar.md-primary.barra-titulo.md-theme-default.md-elevation-5').remove()")
                self.wait_sleep(2)
                self.data['found'] = True
                self.data['evidence'] = self.take_evidence()
                self.data['alertas'] = 1
            elif (msg == 'CNPJ não encontrado'):
                console('Passou pelo captcha corretamente gerando alerta')
                self.data['alertas'] = 0
            else:
                raise Exception('Falha ao resolver o captcha, erro inesperado.')
        else:
            console("quebra recaptcha falhou, erro: " + solver.error_code)
            raise Exception('Erro na comunicação com o fornecedor de solução de captcha. ' + solver.error_code)

        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Bacen')
    def bacen(self):
        self.data['found'] = True
        check_class_file = self.page.query_selector('//*[@class="textoPrincipal"]')
        check_msg_error = self.page.query_selector('//*[@class="msgErro"]')
        console(check_class_file)
        if check_class_file != None:
            self.data['evidence'] = self.take_evidence()
            self.data['result'] = self.page.query_selector('//*[@class="textoPrincipal"]').inner_text()
            self.data['alertas'] = 0
        elif (check_msg_error != None and self.page.query_selector('//*[@class="msgErro"]').inner_text() != 'Digite corretamente o código mostrado na imagem') :
            self.data['evidence'] = self.take_evidence()
            self.data['result'] = None
            self.data['alertas'] = 1
        else :
            raise Exception('Após 4 tentativas o captcha não foi resolvido')

        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Clicar TRF1 PJ')
    def clicar_trf1_pj(self):
        self.page.locator('text=Considerar Matriz e Filiais').click()

    @keyword('Clicar TRF1')
    def clicar_trf1(self):
        self.page.query_selector('body > pgp-root > div > pgp-certidao > pgp-solicitacao-certidao > div > h3').click()
        self.wait_sleep(10)
        self.page.query_selector('body > pgp-root > div > pgp-certidao > pgp-solicitacao-certidao > div > form > div > div > button > span').click()
        self.wait_sleep(40)
        self.data['found'] = True
        check_certidao = self.page.query_selector('//*[@class="certidao-viewer"]')
        check_alerta = self.page.query_selector('body > pgp-root > div > pgp-certidao > pgp-solicitacao-analise-form > div.info > p.aviso > strong')
        if check_certidao != None:
            # with self.page.expect_download() as download_info:
            #     self.page.query_selector('body > pgp-root > div > pgp-certidao > pgp-certidao-viewer > div > button').click()
            # download = download_info.value
            # console(download.path())
            # data = open(download.path(), "rb").read()
            # evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            # console(evidence_b64)
            self.data['evidence'] = self.take_evidence()
            self.data['alertas'] = 0
        elif check_alerta != None:
            self.data['evidence'] = self.take_evidence()
            self.data['alertas'] = 1
        else :
            raise Exception('Resultado não esperado, fluxo fora do definido.')
        write_results(json.dumps(self.data, ensure_ascii=False))

    @keyword('Resolver captcha imagem TRF5')
    def resolver_captcha_imagem_trf(self,selector: str, input: str, click:str, retry: int = 0):
        console('Resolvendo captcha Imagem')
        self.page.wait_for_selector(selector)
        card = self.page.query_selector(selector)
        result = card.screenshot()
        solver = dataUriCaptcha()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(result))
        console(captcha_text)
        if captcha_text != 0:
            console("captcha text "+captcha_text)
            self.captcha = captcha_text
            self.data['captcha'] = captcha_text
            self.page.fill(input, captcha_text)

            self.page.query_selector(click).click()
            self.wait_sleep(30)
            try:
                teste = self.page.query_selector('//*[@id="form:dialogCertidaoDistribuicao1_content"]')
                if teste.is_visible() :
                    console('captcha funcionou')
            except Exception as e:
                console('Tentando novamente, deu erro de tempo ou captcha errado')
                console(str(e))
                if retry < 3:
                    self.resolver_captcha_imagem_trf(selector, input, click, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    self.data['found'] = False
                    raise Exception('Erro após 4 tentativas de resolver o captcha')
        else:
            raise Exception('Erro na comunicação com o fornecedor de resolver captcha')

    @keyword('Resolver Download TRF5')
    def download_trf5(self):
        self.wait_sleep(15)
        self.data['found'] = True
        check_process = self.page.query_selector('//*[@id="form:j_idt173"]')
        check_ok = self.page.query_selector('//*[@id="form:j_idt159"]')
        # process.env.DEBUG = 'pw:api,pw:browser*'
        if check_process.is_visible():
            console('tem processo')
            self.data['alertas'] = 1
            self.data['result'] = self.page.query_selector('//*[@id="form:labelTipoRetorno3"]').inner_text()
            self.wait_sleep(20)
            with self.page.expect_download() as download_info:
                self.page.query_selector('//*[@id="form:j_idt173"]').click()
            download = download_info.value
            console(download.path())
            data = open(download.path(), "rb").read()
            evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            console(evidence_b64)
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            console(self.data)
            write_results(json.dumps(self.data, ensure_ascii=False))
        elif check_ok.is_visible():
            self.data['alertas'] = 0
            self.wait_sleep(20)
            with self.page.expect_download() as download_info:
                self.page.query_selector('//*[@id="form:j_idt159"]').click()
            download = download_info.value
            console(download.path())
            data = open(download.path(), "rb").read()
            evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
            console(evidence_b64)
            self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
            console(self.data)
            write_results(json.dumps(self.data, ensure_ascii=False))
        else :
            raise Exception('resultado fora do esperado')

    @keyword('RecaptchaV2 TRF3')
    def recaptchaV2_trf3(self, site_url: str, website_key: str, retry: int = 0):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        solver.set_website_url(site_url)
        solver.set_website_key(website_key)
        g_response = solver.solve_and_return_solution() #resposta do captcha
        if g_response != 0:
            console("Inserindo resposta do captcha no textArea...")

            self.page.eval_on_selector('#g-recaptcha-response', '(el) => el.value =' +"'"+ g_response +"'")

            self.wait_sleep(10)
            self.page.query_selector('//*[@id="submit"]').click()
            BuiltIn().sleep('5000ms')

            if self.page.query_selector('//*[@id="modal-carregamento-certidao"]/div/div/div/div') != None:
                while self.page.query_selector('//*[@id="modal-carregamento-certidao"]/div/div/div/div').is_hidden() != True:
                    console('Modal de processamento continua aberto, entidade grande ')
                    console("Esperando a resposta")
                    BuiltIn().sleep('15000ms')
                    if self.page.query_selector('//*[@id="modal-carregamento-certidao"]/div/div/div/div') == None:
                        break
            console('Analisando resultado...')
            check_certidao = self.page.query_selector('//*[@id="ContainerImpressaoCertidao"]')
            check_dados_adicionais = self.page.query_selector('body > div > main > div.text-center > div > div > h5')
            errors = self.page.query_selector('//*[@id="encapsula_erros"]')

            if check_certidao != None or check_dados_adicionais != None and errors == None:
                self.data['found'] = True
                check_processo = self.page.query_selector_all('//*[@class="registro-processo"]')
                console(check_processo)
                if not check_processo and check_dados_adicionais == None:
                    self.data['evidence'] = self.take_evidence()
                    self.data['alertas'] = 0
                else :
                    self.data['evidence'] = self.take_evidence()
                    self.data['alertas'] = 1
            else :
                console('Tentando novamente, deu erro de tempo ou recaptcha errado')
                if retry < 3:
                    self.recaptchaV2_trf3(site_url, website_key, retry+1)
                else:
                    console('Finalizando após 4 tentativas')
                    raise Exception('Erro após 4 tentativas')

        else :
            console("quebra recaptcha falhou, erro: " + solver.error_code)
            raise Exception('Erro na comunicação com o fornecedor de solução de captcha. ' + solver.error_code)

        write_results(json.dumps(self.data, ensure_ascii=False))

    def check_is_odd(self, number):
        num = int(number)
        if (num % 2) == 0:
            return False
        return True

    @keyword('Pegar dados da tabela Uruguai')
    def tabela_uruguai(self, paginacao: str):
        self.data['found'] = True
        self.data['resultados'] = []
        console(self.page.query_selector(paginacao))
        if self.page.query_selector(paginacao) != None:
            dados_brutos = self.page.query_selector(paginacao).inner_text()
            dado_refinado = dados_brutos.split('/ ')
            paginas = dado_refinado[1].split(' (')
            selector = '.iceDatTblRow'
            pagina_atual = 1
            pagina_final = paginas[0].replace(",","")
            console( pagina_final)
            pegar_conteudo = True
            while pegar_conteudo:
                BuiltIn().sleep('1500ms')
                self.page.wait_for_selector(selector)
                table_lines = self.page.query_selector_all(selector)
                console("a pagina atual é ")
                console(pagina_atual)
                for line in table_lines:
                    dados = {}
                    pais = line.query_selector('td:nth-child(1)').inner_text()
                    identificacao = line.query_selector('td:nth-child(2)').inner_text()
                    denominacao_social = line.query_selector('td:nth-child(3)').inner_text()
                    domicilio_fiscal = line.query_selector('td:nth-child(4)').inner_text()
                    estado_do_provedor = line.query_selector('td:nth-child(5)').inner_text()
                    dados['pais'] = pais
                    dados['identificacao'] = identificacao
                    dados['denominacao_social'] = denominacao_social
                    dados['domicílio_fiscal'] = domicilio_fiscal
                    dados['estado_provedor'] = estado_do_provedor
                    self.data['resultados'].append(dados)
                if len(self.data['resultados']) == 200:
                    console('Finalizando pois atingiu a quantidade máxima')
                    pegar_conteudo = False
                else :
                    if pagina_atual != int(pagina_final):
                        console('indo para proxima pagina')
                        self.page.query_selector('//*[@id="formularioVacioPublico:paginadorBusqedaProveedorArribanext"]').click()
                        BuiltIn().sleep('1500ms')
                        pagina_atual += 1
                    else :
                        console('Finalizando o loop de while pois chegamos na última p')
                        pegar_conteudo = False
        self.data['alerta'] = len(self.data['resultados'])
        write_results(json.dumps(self.data, ensure_ascii=False))
    def handler(self, page):
        page.wait_for_load_state('networkidle')
        console(page.url)
        console(page.title)
        with page.expect_download() as download_info:
            page.click('#icon > iron-icon')
        download = download_info.value
        console(download.path())
        self.wait_sleep(15)
        data = open(download.path(), "rb").read()
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(data).decode('utf-8'))
        console(evidence_b64)
        self.data['evidence'] = 'data:application/pdf;base64,{}'.format(evidence_b64)
        console(self.data)
        self.wait_sleep(15)
        self.page.close()
        self.browser.close()
        self.playwright.stop()
    def add_letter(self, string, letter):
        result = ""
        for i in range(0, len(string), 4):
            result += string[i:i+4] + letter
        return result
    def mascara_cpf(self, cpf):
        cpf_formatado = '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
        return cpf_formatado

    @keyword('Quitacao Participacao Eleitor')
    def quitacao_participacao_eleitor(self, cpf, titulo, nome,retry:int = 0):
        self.data['found'] = True
        self.data['alertas'] = 0
        if titulo == "":
            write_results(json.dumps(self.data, ensure_ascii=False))
        else :
            nome_tratado = nome.replace(' ', '+')
            console(nome_tratado)
            titulo_tratado = self.add_letter(titulo, "+")
            titulo_tratado = titulo_tratado[:-1]
            console(titulo_tratado)
            # cpf_tratado = self.mascara_cpf(cpf)
            cpf_tratado = cpf
            console(cpf_tratado)
            console('Enviando requisição...')
            body = {}
            url = "https://sgip3.tse.jus.br/sgip3-consulta/api/v1/participaOrgaoPartidario/relatorioNegativoOrgaoPartidario?cpfEleitor="+cpf_tratado+"&nomeEleitor="+nome_tratado+"&tituloEleitor="+titulo_tratado
            console(url)
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Content-Type": "application/json; charset=utf-8"
            }
            response = requests.get(url, json= body, headers= headers)

            console("response status code: " +  str(response.status_code)+"\n\n")
            if response.status_code == 200:
                contents = json.loads(response.content)
                console(contents)
                historico = []
                for content in contents:
                    console("esse é o content atual do for")
                    console(content)
                    if content['sigla'] != 'None' and content['sigla'] != None:
                        self.data['alertas'] += 1
                        content['alerta'] = True
                    else :
                        content['alerta'] = False
                    historico.append(content)
                self.data['historico'] = historico
                console(self.data)
                write_results(json.dumps(self.data, ensure_ascii=False))
            else :
                if retry < 3:
                    console('tentando mais uma vez pois o resultado veio diferente do esperado')
                    self.quitacao_participacao_eleitor(cpf, titulo, nome, retry+1)
                else :
                    raise Exception('resultado fora do esperado requisição retornou algo diferente de 200', response)
