*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Compras Publicas Ecuador
    Abrir o navegador em                       https://comprar.gob.ar/PLIEGO/BuscarProveedorCiudadano.aspx  False
    Digitar texto em campo                     ${razon_social}  \#ctl00_CPH1_UCBuscarProveedor_txtRazonSocial
    Clicar em                                  \#ctl00_CPH1_UCBuscarProveedor_btnBusquedaAvanzada
    Extrair resultados ComprarArgentina
    [Teardown]  Fechar navegador e parar playwright