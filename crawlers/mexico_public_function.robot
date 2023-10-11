*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em Función Publica
    Abrir o navegador em                       https://compras.funcionpublica.gob.mx/ConsultaPublicaDGRSP/    false    5000
    Clicar em                                  //*[@id="j_id10:tablaConsultas:0:col_1"]/a
    Digitar texto em campo                     ${name}  //*[@id="consultaForm:j_id32:0:s4nci0n_InputText"]
    Clicar em                                  //*[@id="consultaForm:j_id32:generarConsulta"]
    Pegar dados mexico em JSON                 //*[@id="j_id43:tbl"]
    [Teardown]  Fechar navegador e parar playwright
