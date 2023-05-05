*** Settings ***
Library  ../core/robot-libs/ConsultaMexico.py


*** Tasks ***
Consulta Mexico Pj
    Consulta Mexico                ${razao_social}
