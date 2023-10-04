from robot.api.deco import keyword, library
from robot.api.logger import console
from utils import write_results
from core.env import env
from robot.libraries.BuiltIn import BuiltIn
from playwright.sync_api import sync_playwright
from anticaptchaofficial.recaptchav2proxyless import *
import json
import re
import base64


@library(scope='GLOBAL', version='0.0.1')
class NewCoreLib(object):
    browser = None

    @keyword('Abrir o navegador em')
    def open_browser(self, url: str, headless: bool = True, slow_mo: float = None, navegador: str = 'firefox', ignore_https_errors: bool = False):
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
        self.context = self.browser.new_context(
            ignore_https_errors=ignore_https_errors)
        self.page = self.context.new_page()
        self.page.goto(url, timeout=180000)
        self.data = {}

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

    @keyword('Selecionar')
    def choose(self, element: str, value: str):
        self.page.select_option(element, value)

    @keyword('Seletor')
    def query_selector(self, selector: str):
        return self.page.query_selector(selector)

    @keyword('Esperar download')
    def expect_download(self):
        return self.page.expect_download()

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

    @keyword('Printar tela')
    def take_evidence(self):
        evidence_bytes = self.page.screenshot(full_page=True)
        evidence_b64 = re.sub(r"\n", '', base64.encodebytes(
            evidence_bytes).decode('utf-8'))
        return 'data:image/png;base64,{}'.format(evidence_b64)

<<<<<<< Updated upstream
    @keyword('Esperar')
    def wait_sleep(self, time_to_wait: str|int):
=======
    @keyword("Esperar")
    def wait_sleep(self, time_to_wait):
>>>>>>> Stashed changes
        BuiltIn().sleep(time_to_wait)

    @keyword('RecaptchaV2 TRF4')
    def recaptchaV2(self, site_url: str, website_key: str):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(env('CAPTCHA_KEY'))
        solver.set_website_url(site_url)
        solver.set_website_key(website_key)
        g_response = solver.solve_and_return_solution() #resposta do captcha
        if g_response != 0:
            return g_response
        else:
            console(solver.error_code)
            return False
