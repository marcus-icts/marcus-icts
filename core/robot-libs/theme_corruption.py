BASE_URL = "https://www.guatecompras.gt"


def theme_corruption(page):
    """
    Consulta Fonte de corrupção do Guatecompras
    :return:
    """
    data = []
    table = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_gvInhabilitacionesGuatecompras"]')

    if table is not None:
        rows = table.query_selector_all('tbody > tr.FilaTablaDetalle')

        urls = []
        for row in rows:
            link_element = row.query_selector('td:nth-child(1) > a')
            urls.append(f"{BASE_URL}{link_element.get_attribute('href')}")

        for url in urls:
            result = {}
            page.goto(url)

            page.wait_for_load_state("domcontentloaded")

            motivo = page.query_selector('#MasterGC_ContentBlockHolder_lblMotivo')
            result['motivo'] = motivo.inner_text().strip() if motivo is not None else None

            o_que_provocou = page.query_selector('#MasterGC_ContentBlockHolder_lblHecho')
            result['o_que_provocou'] = o_que_provocou.inner_text().strip() if o_que_provocou is not None else None

            duracao = page.query_selector('#MasterGC_ContentBlockHolder_lblDuracion')
            result['duracao'] = duracao.inner_text().strip() if duracao is not None else None

            inicio = page.query_selector('#MasterGC_ContentBlockHolder_lblFechaCreacion')
            result['inicio'] = inicio.inner_text().strip() if inicio is not None else None

            termino = page.query_selector('#MasterGC_ContentBlockHolder_lblFechaVencimiento')
            result['termino'] = termino.inner_text().strip() if termino is not None else None

            status = page.query_selector('#MasterGC_ContentBlockHolder_lblEstatus')
            result['status'] = status.inner_text().strip() if status is not None else None

            data.append(result)

    return data
