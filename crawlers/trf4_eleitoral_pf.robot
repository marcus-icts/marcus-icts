*** Settings ***
Library  ../core/robot-libs/Trf4.py


*** Variables ***
${TIPO_CERTIDAO}                            //*[@id="frmCertidao"]/fieldset/b/input[3]


*** Tasks ***
Buscar em TRF4 Eleitoral Pf
    trf4                                                    ${cpf}    ${TIPO_CERTIDAO}