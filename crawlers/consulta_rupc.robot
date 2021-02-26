*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Consulta Rupc
    Abrir o navegador em                                                    https://cnet.hacienda.gob.mx/servicios/consultaRUPC.jsf  false
    Clicar em                                                               //*[@id="consulta:tipoSol"]/div[2]
    Clicar em                                                               //*[@id="consulta:tipoSol_panel"]/div/ul/li[3]
    Esperar                                                                 300ms
    Digitar Texto Em Campo                                                  ${razao_social}  //*[@id="consulta:razon"]
    Clicar em                                                               //*[@id="consulta:btnBuscar"]/span
    Esperar até que elemento não esteja visivel                             .ui-datatable-empty-message > td:nth-child(1) > div:nth-child(1)
    Pegar dados da tabela em Hacienda MX JSON passando o seletor do header  //*[@id="formTabla:tabla"]/table/thead/tr[3]  //*[@id="formTabla:tabla_data"]  
    [Teardown]  Fechar navegador e parar playwright
