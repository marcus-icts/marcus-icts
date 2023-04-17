*** Settings ***
Library  ../core/robot-libs/CertidaoDebitosIbama.py


*** Tasks ***
Buscar certidao de debitos ibama pf
    Certidao Debitos Ibama - PF                 ${doc}
