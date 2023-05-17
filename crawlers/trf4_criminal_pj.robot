*** Settings ***
Library  ../core/robot-libs/Trf4.py


*** Variables ***
${TIPO_CERTIDAO}                            //*[@id="frmCertidao"]/fieldset/b/input[2]


*** Tasks ***
Buscar em TRF4 Criminal Pj
    trf4                                                    ${cnpj}    ${TIPO_CERTIDAO}
