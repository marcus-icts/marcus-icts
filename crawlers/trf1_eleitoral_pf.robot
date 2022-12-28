*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TRF5 criminal PF
    Abrir o navegador em                       https://sistemas.trf1.jus.br/certidao/#/solicitacao
    Esperar                                   3
    Clicar em                                 //*[@id="mat-select-0"]
    Esperar                                   3
    Clicar em                                 //*[@id="mat-option-3"]
    Esperar                                   3
    Clicar em                                 //*[@id="mat-chip-list-input-0"]
    Esperar                                   3
    Clicar em                                 //*[@id="mat-option-17"]
    Esperar                                   3
    Digitar texto em campo                    ${cpf}    //*[@id="mat-input-0"]
    Esperar                                   3
    Clicar TRF1
    [Teardown]  Fechar navegador e parar playwright
