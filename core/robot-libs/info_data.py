from robot.api.logger import console


def load_info_data(page):
    """
    Carrega as informações cadastrais e de sócios
    """
    console("Carregando informações cadastrais.")
    result = {}

    cui = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblCUI"]')
    result['cui'] = cui.inner_text().strip() if cui is not None else None

    nombre = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblNombreProv"]')
    result['nombre'] = nombre.inner_text().strip() if nombre is not None else None

    tipo_organizacion = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblTipoOrganizacion"]')
    result['tipo_organizacion'] = tipo_organizacion.inner_text().strip() if tipo_organizacion is not None else None

    nit = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblNIT"]')
    result['nit'] = nit.inner_text().strip() if nit is not None else None

    field_nome_comercial = page.query_selector(
        '#contenido > div:nth-child(4) > .cuadroResumen > div > div:nth-child(6) > div:first-child > span'
    )

    if field_nome_comercial is not None and field_nome_comercial.inner_text().startswith("Nombre Comercial"):
        console("Nome Comercial encontrado.")
        result['nome_comercial'] = field_nome_comercial.inner_text().strip()
    else:
        console("Nome Comercial não encontrado.")
        result['nome_comercial'] = None

    console("Carregando informações adicionais.")

    fecha_de_constitucion = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblFechaConstitucion"]')
    result[
        'fecha_de_constitucion'] = fecha_de_constitucion.inner_text().strip() if fecha_de_constitucion is not None else None

    actividad_economica = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblActividadEconomica"]')
    result[
        'actividad_economica'] = actividad_economica.inner_text().strip() if actividad_economica is not None else None

    console('Carregando informações do domicilio comercial.')

    pagina_web = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblComPagina"]')
    result['pagina_web'] = pagina_web.inner_text().strip() if pagina_web is not None else None

    correo_electronico = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblComCorreo"]')
    result['correo_electronico'] = correo_electronico.inner_text().strip() if correo_electronico is not None else None

    endereco = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblComDireccion"]')
    result['endereco'] = endereco.inner_text().strip() if endereco is not None else None

    telefone = page.query_selector('//*[@id="MasterGC_ContentBlockHolder_lblComTelefono"]')
    result['telefone'] = telefone.inner_text().strip() if telefone is not None else None

    console('Carregando informações dos representantes legais.')
    result['representantes_legais'] = []

    table_representantes = page.query_selector_all(
        '#MasterGC_ContentBlockHolder_gvRepresentantesLegales > tbody > .FilaTablaDetalle'
    )
    for i in range(len(table_representantes)):
        row = table_representantes[i]
        obj = {}

        representante = row.query_selector('td:nth-child(1)')
        obj['representante'] = representante.inner_text().strip() if representante is not None else None

        proveedor = row.query_selector('td:nth-child(2)')
        obj['proveedor'] = proveedor.inner_text().strip() if proveedor is not None else None

        plazo = row.query_selector('td:nth-child(3)')
        obj['plazo'] = plazo.inner_text().strip() if plazo is not None else None

        link_icon = row.query_selector('td:nth-child(4) > a')
        if link_icon is not None:
            link_icon.click()
            try:
                page.wait_for_selector('#MasterGC_ContentBlockHolder_updDetalleRepresentado:visible', timeout=60000)

                infos = page.query_selector_all(
                    '#MasterGC_ContentBlockHolder_wuDetalleRepresentados_gdvDetalleRep > tbody > .FilaTablaDetalle'
                )

                if infos is not None:
                    obj['subrepresentes'] = []
                    for info in infos:
                        key = info.query_selector('td:nth-child(1)')
                        value = info.query_selector('td:nth-child(2)')
                        if key is not None and value is not None:
                            obj['subrepresentes'].append({
                                key.inner_text().strip(): value.inner_text().strip()
                            })
            except Exception as e:
                raise Exception(f"Erro ao carregar informações de subrepresentantes: {e}")

            close_button = page.query_selector('.modal-dialog button.close')
            if close_button:
                close_button.click()

        result['representantes_legais'].append(obj)
        table_representantes = page.query_selector_all(
            '#MasterGC_ContentBlockHolder_gvRepresentantesLegales > tbody > .FilaTablaDetalle'
        )

    return result
