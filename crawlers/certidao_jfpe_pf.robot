*** Settings ***
Library  ../core/robot-libs/CertidaoJfpe.py


*** Tasks ***
Buscar Buscar Justiça Federal do Pernambuco PF
    Certidao JFPE - PF                ${cpf}