*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Quitação Eleitor
    Abrir o navegador em                       https://sgip3.tse.jus.br/sgip3-consulta/#!/orgao-partidario/participa-orgao-partidario    false     000      chromium
    Esperar                                     10
    Digitar texto em campo                          ${nome_titulo}    //html/body/div/div[1]/participa-orgao-partidario/div/div[2]/form/div[2]/input
    Digitar texto em campo                          ${titulo}    //html/body/div/div[1]/participa-orgao-partidario/div/div[2]/form/div[3]/input
    Digitar texto em campo                          ${cpf}    //html/body/div/div[1]/participa-orgao-partidario/div/div[2]/form/div[4]/input
    Esperar                                     5
    Clicar em                                     //html/body/div/div[1]/participa-orgao-partidario/div/div[2]/form/div[5]/button[1]
    Esperar                                     20
    Quitacao Participacao Eleitor               ${cpf}  ${titulo}   ${nome_titulo}

    # [Teardown]  Fechar navegador e parar playwright
