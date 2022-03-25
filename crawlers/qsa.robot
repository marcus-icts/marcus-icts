*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Qsa
    Abrir o navegador em                       http://servicos.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp
    Resolver QsaCaptcha                          ${cnpj}
    [Teardown]  Fechar navegador e parar playwright
