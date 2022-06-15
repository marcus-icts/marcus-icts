*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Comprasal
    Abrir o navegador em                       https://www.comprasal.gob.sv/comprasalweb/proveedores    true   3000
    Digitar texto em campo nome comprasal      ${name}
    Extrair resultados CompraSal
    [Teardown]  Fechar navegador e parar playwright
