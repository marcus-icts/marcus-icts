*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_TSE}                                  https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-crimes-eleitorais


*** Tasks ***
Buscar quitação eleitoral
    crimes eleitorais                                       ${nome}    ${cpf_titulo}    ${data_nascimento}    ${nome_mae}    ${nome_pai}
    [Teardown]  Fechar navegador e parar playwright
