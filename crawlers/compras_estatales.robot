*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_COMPRAS}                                 https://www.comprasestatales.gub.uy/rupe/clientes/publicos/BusquedaPublicaDeProveedoresCliente.jsf
${CAMPO_NOME}                                  //*[@id="formularioVacioPublico:filtroDenomSocial_input"]
${ENVIAR}                                      //*[@id="formularioVacioPublico:buscarProveedoresButton"]/span/span/button
${PAGINACAO}                                   //*[@id="formularioVacioPublico:j_idt41"]

*** Tasks ***
Buscar em Compras Estatales
    Abrir o navegador em                                    ${URL_COMPRAS}
    Esperar                                                                 2
    Digitar Texto Em Campo                                  ${razao_social}     ${CAMPO_NOME}
    Esperar                                                                 5
    Clicar em                                               ${ENVIAR}
    Esperar                                                                 10
    Pegar dados da tabela Uruguai                           ${PAGINACAO}
    [Teardown]  Fechar navegador e parar playwright
