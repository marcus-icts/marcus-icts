*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Oncae Honduras
    Abrir o navegador em                       http://aplicaciones.oncae.gob.hn/Proveedores/BusquedaProveedores.aspx   true    4000
    Selecionar                                  //*[@id="ctl00_cphCuerpo_ddlPais"]  1
    Digitar Texto Em Campo                      ${name}  //*[@id="ctl00_cphCuerpo_txtProveedor"]
    Clicar em                                   //*[@id="ctl00_cphCuerpo_btnBuscar"]
    Honduras
    [Teardown]  Fechar navegador e parar playwright
