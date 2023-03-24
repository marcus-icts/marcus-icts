*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_API_GENERATE}                              https://filia-consulta.tse.jus.br/filia-consulta/api/v1/certidoes/gerar
${WEBSITE_KEY}                          6LfHZq0fAAAAAFNQsEPuE04EdG0ZeEFxhYXUo374

*** Tasks ***
Buscar filiacao partidaria
    Filiacao Partidaria - TSE                 ${URL_API_GENERATE}     ${WEBSITE_KEY}     ${name}     ${voters_card}     ${birth_date}     ${mothers_name}     ${fathers_name}
