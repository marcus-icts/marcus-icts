*** Settings ***
Library  ../core/robot-libs/Guatecompras.py


*** Tasks ***
Buscar em Guatecompras
    crawler    ${nombre}    financeiro
