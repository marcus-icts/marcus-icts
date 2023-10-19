import base64
import json

from core.env import env
from dataUriCaptcha import dataUriCaptcha
from info_data import load_info_data
from theme_corruption import theme_corruption
from theme_finance import theme_finance
from theme_reputation import theme_reputation
from robot.api.deco import keyword, library
from robot.api.logger import console, error
from utils import write_results

import NewCoreLib


@library(scope="GLOBAL", version="0.0.1")
class Guatecompras(NewCoreLib.NewCoreLib):
    """
    Crawler para os temas de corrupção, financeiro e reputacional da fonte Guatecompras (Guatemala).
    """

    # Constantes/variavéis usadas no Crawling
    BASE_URL = "https://www.guatecompras.gt"
    PAGE_URL = "/proveedores/busquedaProvee.aspx"
    HEADLESS = True
    SLOW_MO = 3000

    browser = None
    page = None
    name = None
    entity = None
    list_results = []

    NUMBER_OF_RETRIES = 4

    @keyword("crawler")
    def crawler(self, name, theme):
        """
        Consulta Fonte de corrupção do Guatecompras
        :param name: Nome a ser pesquisado na fonte
        :param theme: Tema a ser pesquisado
        """
        try:
            self.open_browser(f"{self.BASE_URL}{self.PAGE_URL}", self.HEADLESS, self.SLOW_MO)

            self.name = name.upper()
            self.search()
            self.results()

            if len(self.list_results) > 0:
                self.check_entity()

                if self.entity is not None:
                    self.load_data(theme)

            found = len(self.list_results) > 0 and self.entity is not None

            self.data['found'] = found

            write_results(json.dumps(self.data, ensure_ascii=False))

            self.teardown()

        except Exception as e:
            self.teardown()
            raise Exception(e)

    def search(self):
        """
        Preenche o formulário de pesquisa
        """
        console(f"\nBuscando resultados para a consulta: {self.name}")

        input_selector = '//*[@id="MasterGC_ContentBlockHolder_txtNuevaBusquedaNombre"]'
        button_selector = '//*[@id="MasterGC_ContentBlockHolder_cmndNuevaBusquedaNombre"]'

        self.wait_for_element(input_selector)
        self.input_text(self.name, input_selector)
        self.page.query_selector(button_selector).click()

    def results(self):
        """
        Extrai os resultados encontrados na pesquisa
        """

        self.wait_for_element('//*[@id="MasterGC_ContentBlockHolder_Tr1"]')

        table = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_gvResultado"]')
        if table is None:
            console("Nenhum resultado encontrado.")
        else:
            rows = table.query_selector_all("tbody > tr[class^=TablaFilaMix]")
            total = len(rows)

            if total > 0:
                console("Pesquisa realizada com sucesso.")
            else:
                console("Nenhum resultado encontrado.")

            for row in rows:
                columns = row.query_selector_all("td")
                link = columns[0].query_selector("a").get_attribute("href")
                nombre = columns[1].query_selector("li").text_content().strip()
                self.list_results.append({
                    "nombre": nombre,
                    "link": f"{self.BASE_URL}{link}"
                })

    def check_entity(self):
        for row in self.list_results:
            if str(row["nombre"]).upper() == str(self.name).upper():
                self.entity = row
                break

    def load_data(self, theme):
        """
        Carrega os dados detalhados de cada resultado
        :param theme: Tema a ser carregado
        """

        row = self.entity
        console(f"\nCarregando dados para: {row['nombre']}")
        self.page.goto(row["link"])
        self.page.wait_for_load_state("domcontentloaded")

        cloudflare_title = self.page.query_selector('h2#challenge-running')
        if cloudflare_title:
            raise Exception("Cloudflare detectado.")

        if self.has_captcha():
            console("Captcha encontrado.")
            if self.resolve_captcha():
                console("Captcha resolvido com sucesso.")

        self.data |= load_info_data(self.page)

        if theme == "corrupcao":
            console("Carregando informações de corrupção.")

            inabilitados = theme_corruption(self.page)

            if inabilitados:
                self.data["inabilitados"] = inabilitados

        elif theme == "financeiro":
            console("Carregando informações financeiras.")
            self.data |= theme_finance(self.page)

        elif theme == "reputacao":
            console("Carregando informações de reputação.")
            self.data |= theme_reputation(self.page)


    def has_captcha(self):
        """
        Verifica se o captcha está presente na página
        :return: Boolean
        """
        image_selector = '//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaImage"]'
        image_captcha = self.page.query_selector(image_selector)
        return image_captcha is not None

    def resolve_captcha(self, attempt=1):
        """
        Resolve o captcha presente na página
        :param attempt: Número da tentativa atual
        :return: Boolean
        """
        image_captcha = self.page.query_selector(
            '//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaImage"]'
        )
        screenshot = image_captcha.screenshot()
        captcha_text = self.solve_captcha_from_image(screenshot)

        if captcha_text != 0:
            console(f"Captcha - Tentativa ({attempt}): {captcha_text}")
            self.input_text(captcha_text,
                            '//*[@id="MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaTextBox"]')
            self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_btnBuscar"]').click()

            # Espera o loader sumir e a página carregar por completo
            self.wait_sleep(2)
            counter = 0
            loader = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_UpdateProgress1"]')
            details = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblNombreProv2"]')
            while (loader is None or loader.is_visible()) and details is None:
                counter += 1
                self.wait_sleep(2)
                if counter == 10:
                    raise Exception("Tempo de espera excedido.")

                # verifica novamente
                loader = self.page.query_selector('//*[@id="MasterGC_ContentBlockHolder_UpdateProgress1"]')
                details = self.page.query_selector('//*[@id="customColorTextNoSize"]')

            # Verifica se o captcha foi resolvido respeitando o limite de tentativas
            if attempt == self.NUMBER_OF_RETRIES:
                raise Exception("Número máximo de tentativas de resolução de captcha atingido.")

            # Verifica se o captcha foi resolvido
            if self.has_captcha():
                return self.resolve_captcha(attempt + 1)

            return True

    def solve_captcha_from_image(self, image):
        """
        Resolve o captcha da imagem
        :param image: Imagem do captcha
        :return: String
        """
        solver = dataUriCaptcha()
        solver.set_key(env('CAPTCHA_KEY'))
        captcha_text = solver.solve_and_return_solution(base64.encodebytes(image))
        return captcha_text


