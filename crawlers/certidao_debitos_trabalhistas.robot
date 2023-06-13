*** Settings ***
Library  ../core/robot-libs/CertidaoDebitosTrabalhistas.py

*** Tasks ***
Buscar certidao de debitos trabalhistas 
    Certidao Debitos Trabalhistas                 ${doc}
