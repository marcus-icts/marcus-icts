*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Bacen Pf
    Abrir o navegador em                                    https://www3.bcb.gov.br/nadaconsta/emitirCertidaoSancionador    false   4000
    Digitar texto em campo                                  ${cpf}    //*[@id="textFieldCPF8"]
    Resolver captcha imagem                                 //*[@id="imgCodigoa"]   //*[@name="captchaPanel:txtCodigo"]     //*[@id="botaoEmitir3"]     //*[@class="section-to-print"]
    Bacen
    [Teardown]  Fechar navegador e parar playwright
