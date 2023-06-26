*** Settings ***
Library  ../core/robot-libs/AntecedentesCriminais.py


*** Tasks ***
Busca Antecedentes Criminais
    Antecedentes Criminais               ${cpf}     ${name}