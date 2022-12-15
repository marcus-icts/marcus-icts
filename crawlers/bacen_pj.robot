*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Bacen Pj
    Abrir o navegador em                                    https://www3.bcb.gov.br/nadaconsta/emitirCertidaoSancionador
    Esperar                                                 300ms
    Clicar em                                               //*[@title="CNPJ"]
    Esperar                                                 600ms
    Digitar texto em campo                                  ${cnpj}    //*[@name="panelCamposConteudo:containerCNPJ:textFieldCNPJ"]
    Resolver captcha imagem bacen                           //*[@id="imgCodigoa"]   //*[@name="captchaPanel:txtCodigo"]     //*[@id="botaoEmitir3"]     //*[@class="msgErro"]
    Bacen
    [Teardown]  Fechar navegador e parar playwright
