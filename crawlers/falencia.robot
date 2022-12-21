*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Falencia
    Abrir o navegador em                       https://bancofalencia.tst.jus.br/
    Digitar Texto Em Campo                     ${cnpj}  //*[@id="cnpj"]
    Clicar em                                  //*[@id="btPesquisar"]
    Esperar                                    5000ms
    Pegar dados da tabela Falencia
    [Teardown]  Fechar navegador e parar playwright
