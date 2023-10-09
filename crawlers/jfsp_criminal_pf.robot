*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_TRF3}                                 https://web.trf3.jus.br/certidao-regional/CertidaoCivelEleitoralCriminal/SolicitarDadosCertidao
${CAMPO_TIPO_CERTIDAO}                      //*[@id="Tipo"]
${TIPO_CERTIDAO}                            CRIMINAL
${CAMPO_TIPO_DOCUMENTO}                     //*[@id="TipoDeDocumento"]
${TIPO_DOCUMENTO}                           CPF
${CAMPO_DOCUMENTO}                          //*[@id="Documento"]
${CAMPO_NOME}                               //*[@id="Nome"]
${CAMPO_ABRANGENCIA}                        //*[@id="TipoDeAbrangencia"]
${TIPO_ABRANGENCIA}                         SJSP
${WEBSITE_KEY}                              6Le_CtAZAAAAAEbTeETvetg4zQ7kJI0NH5HNHf1X


*** Tasks ***
Buscar em Jfsp Criminal Pf
    Abrir o navegador em                                    ${URL_TRF3}
    Esperar                                                 2
    Selecionar                                              ${CAMPO_TIPO_CERTIDAO}  ${TIPO_CERTIDAO}
    Selecionar                                              ${CAMPO_TIPO_DOCUMENTO}  ${TIPO_DOCUMENTO}
    Digitar Texto Em Campo                                  ${cpf}  ${CAMPO_DOCUMENTO}
    Esperar                                                 3
    Selecionar                                              ${CAMPO_ABRANGENCIA}  ${TIPO_ABRANGENCIA}
    Esperar                                                 2
    RecaptchaV2 TRF3                                        ${URL_TRF3}     ${WEBSITE_KEY}
    [Teardown]  Fechar navegador e parar playwright
