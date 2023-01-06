*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_TRF2}                                 https://certidoes.trf2.jus.br/certidoes/#/principal/solicitar
${TIPO_CERTIDAO}                            //*[@id="router-view-principal"]/div/div/div/div[2]/div[1]
${OPCAO_JUDICIAL_ELEITORAL}                 //html/body/div[3]/div/ul/li[2]/button
${CAMPO_CPF_CNPJ}                           //*[@id="identificacao"]
${EMITIR_CERTIDAO}                          //*[@id="router-view-principal"]/div/div/div/div[4]/div[2]/button/div
${TEXT_AREA_CAPTCHA_RESPONSE}               //*[@id="g-recaptcha-response"]
${BTN_CONFIRMAR_CAPTCHA}                    //*[@id="recaptcha-verify-button"]
${WEBSITE_KEY}                              6LdHlgshAAAAAGGaHJXAN3sOwdDxVPqazHx9TgRx


*** Tasks ***
Buscar em TRF2 Eleitoral PF
    Abrir o navegador em                                    ${URL_TRF2}            
    Esperar                                                 2
    Clicar em                                               ${TIPO_CERTIDAO}
    Esperar                                                 1
    Clicar em                                               ${OPCAO_JUDICIAL_ELEITORAL}
    Esperar                                                 1
    Digitar Texto Em Campo                                  ${cpf}  ${CAMPO_CPF_CNPJ}
    Esperar                                                 1
    Clicar em                                               ${EMITIR_CERTIDAO}
    Esperar                                                 3
    Resolver imagem recaptchaV2                             ${URL_TRF2}     ${WEBSITE_KEY}
    Esperar                                                 3
    [Teardown]  Fechar navegador e parar playwright
