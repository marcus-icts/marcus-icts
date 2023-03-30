*** Settings ***
Library  ../core/robot-libs/CertidaoEmbargos.py


*** Tasks ***
Buscar certidao embargos pj
    Certidao Embargos - PJ               ${cnpj}