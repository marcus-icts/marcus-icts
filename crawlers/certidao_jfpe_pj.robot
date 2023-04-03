*** Settings ***
Library  ../core/robot-libs/CertidaoJfpe.py


*** Tasks ***
Buscar Justiça Federal do Pernambuco PJ
    Certidao JFPE - PJ                 ${cnpj}