*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Latam tema reputacional
    Abrir o navegador em                                 https://www.guatecompras.gt/proveedores/busquedaProvee.aspx    true    3000
    Digitar Texto Em Campo                               ${nombre}  //*[@id="MasterGC_ContentBlockHolder_txtNuevaBusquedaNombre"]
    Resolver Captcha
    Dados Cadastrais e societários latam
    Tema Reputacional
    [Teardown]  Fechar navegador e parar playwright
