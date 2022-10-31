*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Falencia
    Abrir o navegador em                       https://bancofalencia.tst.jus.br/    false   4000
    Digitar Texto Em Campo                     ${cnpj}  //*[@id="cnpj"]
    Clicar em                                  //*[@id="btPesquisar"]
    Pegar dados da tabela Falencia
    [Teardown]  Fechar navegador e parar playwright
