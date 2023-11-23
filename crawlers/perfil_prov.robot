*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Perfil Prov
    Abrir o navegador em                       https://apps.osce.gob.pe/perfilprov-ui   false    3000
    Digitar texto em campo                     ${ruc}    //*[@id="textBuscar"]
    Clicar em                                  //*[@id="btnBuscar"]/i
    Pegar dados da página perfilProv
    [Teardown]  Fechar navegador e parar playwright
