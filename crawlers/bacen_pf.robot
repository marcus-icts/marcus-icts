*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Bacen Pf
    Abrir o navegador em                                    https://www3.bcb.gov.br/nadaconsta/emitirCertidaoRegesp
    Digitar texto em campo                                  ${cpf}    //*[@name="panelCamposConteudo:containerCPF:textFieldCPF"]
    Resolver captcha imagem bacen                           //*[@alt="Código"]   //*[@name="captchaPanel:txtCodigo"]     //*[@value="Emitir"]     //*[@class="msgErro"]
    Bacen
    [Teardown]  Fechar navegador e parar playwright
