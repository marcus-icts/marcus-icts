*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Quitação Eleitor
    Abrir o navegador em                       https://sgip3.tse.jus.br/sgip3-consulta/#!/orgao-partidario/participa-orgao-partidario    true     000      chromium
    Quitacao Participacao Eleitor               ${cpf}  ${titulo}   ${nome_titulo}
    [Teardown]  Fechar navegador e parar playwright
