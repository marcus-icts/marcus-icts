*** Settings ***
Library  ../core/robot-libs/CertidaoEmbargos.py


*** Tasks ***
Buscar certidao embargos pf
    Certidao Embargos - PF               ${cpf}