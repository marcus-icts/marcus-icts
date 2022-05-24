*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em FGTS
    Abrir o navegador em                       https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf   true    1000   chromium
    Digitar Texto Em Campo                                                  ${cnpj}  //*[@id="mainForm:txtInscricao1"]
    Resolver captcha imagem FGTS                          0
    Capturar Texto FGTS
    [Teardown]  Fechar navegador e parar playwright
