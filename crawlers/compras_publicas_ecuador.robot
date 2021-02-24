*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Compras Publicas Ecuador
    Abrir o navegador em                       https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/EP/BusquedaProveedorCpc.cpe
    Clicar em                                  .cc-btn
    Digitar texto em campo                     ${razao_social}  \#txtRazonSocial
    Clicar em                                  \#formRadio > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)
    Esperar até que elemento esteja visivel    \#Exportar_a_Excel1
    Pegar dados da tabela em JSON              \#Exportar_a_Excel1  2  3
    Fechar o navegador
    [Teardown]  Fechar navegador e parar playwright
