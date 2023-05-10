*** Settings ***
Library  ../core/robot-libs/Trf4.py


*** Variables ***
${TIPO_CERTIDAO}                            //*[@id="frmCertidao"]/fieldset/b/input[1]


*** Tasks ***
Buscar em TRF4 Civel Pf
    trf4                                                    ${cpf}    ${TIPO_CERTIDAO}
