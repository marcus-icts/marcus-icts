*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TRF5 criminal PF
    Abrir o navegador em                       https://certidoes.trf5.jus.br/certidoes/paginas/certidaodistribuicao.faces
    Digitar texto em campo                          ${nome}     //*[@id="form:nome"]
    Digitar texto em campo                          ${cpf}    //*[@id="form:cpfCnpj"]
    Clicar em                                       //*[@id="form:j_idt66:2"]
    Resolver captcha imagem TRF5                    //*[@id="form:captcha"]     //*[@id="form:jcaptcha"]    //*[@id="form:validar"]/span
    Resolver Download TRF5
    [Teardown]  Fechar navegador e parar playwright
