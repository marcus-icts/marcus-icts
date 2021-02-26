*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Compras Publicas Ecuador
    Abrir o navegador em                       https://www.comprasal.gob.sv/comprasal_web/listaProveeedores
    Digitar texto em campo                     ${name}  input.ui-inputfield:nth-child(1)
    Clicar em                                  table + button:first-of-type
    Extrair resultados CompraSal
    [Teardown]  Fechar navegador e parar playwright