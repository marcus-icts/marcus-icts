import base64
import re

from robot.api.logger import console

from utils import convert_currency


def theme_finance(page):
    """
    Consulta Fonte Financeira do Guatecompras
    :return:
    """

    result = {}

    table = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_div7"]')

    if table:
        link_tabs = table.query_selector_all('ul > li > a.rtsLink')

        if len(link_tabs) > 0:
            for tab in link_tabs:
                title_tab = tab.query_selector('span.rtsTxt')
                if title_tab and title_tab.inner_text().strip() == "NOGS y NPGS":
                    tab.click()
                    break

    evidence_image = page.screenshot(full_page=True)
    evidence_b64 = re.sub(r"\n", "", base64.encodebytes(evidence_image).decode("utf-8"))

    console("Criando evidência.")
    result["evidence"] = "data:image/png;base64,{}".format(evidence_b64)
    result["url"] = page.url

    money = page.query_selector('#MasterGC_ContentBlockHolder_dbResumen > tbody > tr.FooterTablaDetalle')

    if money:
        console("Convertendo moeda.")
        total_money = money.query_selector('td:nth-child(7)')

        if total_money:
            total_money = "{:.2f}".format(float(total_money.inner_text().strip().replace(",", "")))
            money_transformed = convert_currency(page, total_money, "GTQ", "USD")

            result['valor_recebido'] = total_money
            result['valor_usd'] = money_transformed

    return result
