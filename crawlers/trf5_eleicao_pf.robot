*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TRF5 criminal PF
    Abrir o navegador em                       https://certidoes.trf5.jus.br/certidoes2022/paginas/certidaoeleitoral.faces  false   4000
    Selecionar                                  //*[@id="form:orgaoInternet"]  1
    Digitar texto em campo                          ${cpf}      //*[@id="form:cpfCnpj"]
    Clicar em                                       //*[@id="form:padPanel_content"]/div/span
    Esperar                                         12
    Clicar em                                       //*[@id="j_idt11"]/span
    Resolver captcha imagem TRF5                    //*[@id="form:captcha"]     //*[@id="form:jcaptcha"]    //*[@id="form:validar"]/span
    Resolver Download TRF5 Eleitoral
    [Teardown]  Fechar navegador e parar playwright
