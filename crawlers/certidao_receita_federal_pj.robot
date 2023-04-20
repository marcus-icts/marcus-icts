*** Settings ***
Library  ../core/robot-libs/CertidaoReceitaFederalPj.py


*** Tasks ***
Buscar Receita Federal PJ
    Certidao Receita Federal PJ                ${cnpj}
