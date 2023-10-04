import json
import math
import requests

from robot.api.deco import keyword, library
from robot.api.logger import console, error

import NewCoreLib

from time import sleep
from requests.exceptions import Timeout
from utils import write_results


@library(scope="GLOBAL", version="0.0.1")
class CompraSal(NewCoreLib.NewCoreLib):
    # Constantes usadas para o Crawling da API
    PAGE_URL = "https://unac.mh.gob.sv/comprasalweb/proveedores"
    API_URL = "https://unacv2.mh.gob.sv/comprasalmicro/portalpublico/api/v1"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    API_PAGE_SIZE = 50
    API_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://unac.mh.gob.sv",
        "Referer": "https://unac.mh.gob.sv/",
        "User-Agent": USER_AGENT,
        "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }
    DEFAULT_TIMEOUT = 30
    DEFAULT_SLEEP = 60
    MAX_RETRIES = 4

    def __init__(self):
        """
        Inicializa o serviço do playwright e executa o navegador.
        :return: None
        """
        if self.browser is None:
            try:
                self.open_browser("about:blank")
            except Exception:
                pass  # Evita que o Script quebre se não for possível abrir o navegador

    @keyword("comprasal")
    def comprasal(self, name: str):
        """
        Consulta a API do CompraSal (El Salvador).
        :param name: Termo a ser pesquisado na API
        :return: None
        """
        # Variavéis de controle
        page = 1
        records = None
        rows = []
        results = []

        while page <= math.ceil((records or self.API_PAGE_SIZE) / self.API_PAGE_SIZE):
            data = {
                "page": page,
                "size": self.API_PAGE_SIZE,
                "nombre": str(name).upper(),
            }

            console(f"\nBuscando página {page} de resultados para a consulta {name}")
            search_response = self.make_request(
                url=f"{self.API_URL}/proveedores", method="POST", data=data
            )

            if search_response is not None and search_response.status_code == 200:
                search_result = search_response.json()
                records = search_result["totalRecords"]

                # Obtendo os ids da página atual
                for row in search_result["content"]:
                    rows.append(
                        {
                            "id": row["id"],
                            "nombre": row["nombre"],
                        }
                    )
            else:
                error(f"Falhou em buscar dados na página {page}")

            page += 1

        self.show_message_total_results(records)

        # Buscando os dados de cada id
        for key, row in enumerate(rows):
            current_id = str(row["id"])
            current_name = str(row["nombre"]).upper()

            console(f"\nObtendo dados({key+1}): {current_id} - {current_name}")
            data_response = self.make_request(
                url=f"{self.API_URL}/proveedores/{current_id}",
            )

            if data_response is not None and data_response.status_code == 200:
                data_result = data_response.json()
                nome_comercial = str(data_result["nombreComercial"]).upper()

                provider_details = data_result.copy()
                del provider_details["nombre"]
                del provider_details["nombreComercial"]
                del provider_details["obsList"]

                service_details = data_result["obsList"].copy()

                results.append(
                    {
                        "nombre": current_name,
                        "comercial": nome_comercial,
                        "detalles_del_provedor": provider_details,
                        "bienes_obras_servicos": service_details,
                        "evidence": self.evidence(f"{self.PAGE_URL}/{current_id}"),
                    }
                )
            else:
                error(f"Falhou ao obter informações do ID: {id}")

        self.show_message_total_results(records)

        write_results(json.dumps({"data": results}, ensure_ascii=False))

    def make_request(self, url, method="GET", data=None):
        """
        Realiza uma requisição HTTP.
        :param url: Endereço da requisição
        :param method: Método HTTP da requisição
        :param data: Dados a serem enviados na requisição
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        attempts = 0
        response = None

        while attempts < self.MAX_RETRIES:
            try:
                console(f"[{method}] {url}")
                response = requests.request(
                    method,
                    url,
                    headers=self.API_HEADERS,
                    json=data,
                    timeout=self.DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                break
            except Timeout:
                attempts += 1
                error(
                    f"Tempo de espera da solicitação excedido - tentativa {attempts} de {self.MAX_RETRIES}"
                )
                sleep(self.DEFAULT_SLEEP)
                continue
            except Exception:
                attempts += 1
                error(
                    f"Erro na solicitação - tentativa {attempts} de {self.MAX_RETRIES}"
                )
                sleep(self.DEFAULT_SLEEP)
                continue

        return response

    def show_message_total_results(self, results: int):
        """
        Exibe uma mensagem com o total de resultados
        :return: None
        """
        if results is None or results == 0:
            console("\nNenhum resultado encontrado")
        elif results == 1:
            console("\nUm resultado encontrado")
        else:
            console(f"\n{results} resultados encontrados")

    def evidence(self, url: str):
        """
        Tira um screenshot da página pesquisada e retorna o base64.
        :return: Base64 da imagem
        :rtype: str
        """
        if self.browser is not None:
            try:
                self.page.goto(url, timeout=self.DEFAULT_TIMEOUT * 1000)
                self.wait_for_element("body > app-root div.container")
                return self.take_evidence()
            except Exception:
                return ""  # Evita que o Script quebre se não for possível tirar o screenshot
        else:
            return ""  # Retorna screenshot vazio se não for possivel abrir o navegador

    def __del__(self):
        """
        Fecha o navegador e para o serviço do playwright.
        :return: None
        """
        if self.browser is not None:
            try:
                self.teardown()
            except Exception:
                pass  # Evita que o Script quebre se não for possível fechar o navegador
