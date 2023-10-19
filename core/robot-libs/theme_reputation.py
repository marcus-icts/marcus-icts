import base64
import re

from robot.api.logger import console


def theme_reputation(page):
    """
    Consulta Fonte Reputacional do Guatecompras
    :return:
    """

    result = {}

    table = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_div7"]')

    if table:
        link_tabs = table.query_selector_all('ul > li > a.rtsLink')

        if len(link_tabs) > 0:
            for tab in link_tabs:
                title_tab = tab.query_selector('span.rtsTxt')
                if title_tab and title_tab.inner_text().strip() == "Inconformidades":
                    tab.click()
                    break

    evidence_image = page.screenshot(full_page=True)
    evidence_b64 = re.sub(r"\n", "", base64.encodebytes(evidence_image).decode("utf-8"))

    console("Criando evidência.")
    result["evidence"] = "data:image/png;base64,{}".format(evidence_b64)
    result["url"] = page.url

    counter = 0

    inconformidades_infos = table.query_selector_all(
        '#MasterGC_ContentBlockHolder_gvInconformidades > tbody > tr.FilaTablaDetalle'
    )

    if inconformidades_infos:
        for inconformidade in inconformidades_infos:
            if inconformidade.query_selector('span.TablaItemAzulSm').inner_text() == 'Aceptada':
                counter += 1

    result['inconformidades_aceitas'] = counter

    return result
