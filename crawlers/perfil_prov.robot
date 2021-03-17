*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Perfil Prov
    Abrir o navegador em                                 https://apps.osce.gob.pe/perfilprov-ui/
    Digitar Texto Em Campo                               ${ruc}  //*[@id="textBuscar"]
    Clicar em                                            //*[@id="btnBuscar"]
    Pegar dados da página perfilProv
    [Teardown]  Fechar navegador e parar playwright
