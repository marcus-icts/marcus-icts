*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_TRF}                                  https://www2.trf4.jus.br/trf4/processos/certidao/index.php
${TIPO_CERTIDAO}                            //*[@id="frmCertidao"]/fieldset/b/input[1]
${CAMPO_DOCUMENTO}                          //*[@id="string_cpf"]
${WEBSITE_KEY}                              6Ldv-vIUAAAAAN2v6GbNs9w5HTS0HTTLhFL8dDB8


*** Tasks ***
Buscar em TRF4 Civel Pf
    Abrir o navegador em                                    ${URL_TRF}
    Esperar                                                 2
    Digitar Texto Em Campo                                  ${cpf}  ${CAMPO_DOCUMENTO}
    Esperar                                                 3
    Clicar em                                               ${TIPO_CERTIDAO}
    Esperar                                                 3
    RecaptchaV2 TRF4                                        ${URL_TRF}     ${WEBSITE_KEY}   ${cpf}  ${CAMPO_DOCUMENTO}  ${TIPO_CERTIDAO}
    [Teardown]  Fechar navegador e parar playwright
