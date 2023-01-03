*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TRF5 partes PJ
    Abrir o navegador em                       https://certidoes.trf5.jus.br/certidoes2022/paginas/certidaodistribuicaoparte.faces  false   4000
    Selecionar                                  //*[@id="form:orgaoInternet"]  1
    Digitar texto em campo                          ${cnpj}    //*[@id="form:cpfCnpj"]
    Clicar em                                   //*[@id="form:padPanel_content"]
    Esperar                                     4
    Clicar em                                   //*[@id="j_idt15"]
    Esperar                                     4
    Clicar em                                   //*[@id="form:j_idt118"]
    Resolver captcha imagem TRF5                    //*[@id="form:captcha"]     //*[@id="form:jcaptcha"]    //*[@id="form:validar"]/span
    Resolver Download TRF5
    [Teardown]  Fechar navegador e parar playwright
