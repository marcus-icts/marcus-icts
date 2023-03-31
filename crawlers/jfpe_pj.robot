*** Settings ***
Library  ../core/robot-libs/Jfpe.py


*** Variables ***
${URL_API_GENERATE}                              https://filia-consulta.tse.jus.br/filia-consulta/api/v1/certidoes/gerar
${WEBSITE_KEY}                          6LfHZq0fAAAAAFNQsEPuE04EdG0ZeEFxhYXUo374

*** Tasks ***
Buscar Justiça Federal do Pernambuco PJ
    JFPE - PJ                 ${cnpj}
