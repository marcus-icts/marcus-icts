*** Settings ***
Library  ../core/robot-libs/CoreLib.py

*** Tasks ***
Buscar em Perfil Prov
    Abrir o navegador em                                 https://apps.osce.gob.pe/perfilprov-ui/
    Esperar                                              500ms
    Digitar Texto Em Campo                               ${ruc}  //*[@id="textBuscar"]
    Esperar                                              500ms
    Clicar em                                            //*[@id="btnBuscar"]
    Esperar                                              500ms
    Esperar até que elemento esteja visivel              //*[@id="idPanelA2"]/div[2]/div/app-tile/a/div
    Esperar                                              1000ms
    Clicar em                                            //*[@id="idPanelA2"]/div[2]/div/app-tile/a/div
    Esperar                                              2000ms
    Pegar dados da página perfilProv                     //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[1]/div[2]/div/div[1]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/div[1]/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/ul[1]/li/div/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/div[1]/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/div[2]/div/span/a  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/ul[2]/li[1]/div/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/ul[2]/li[3]/div/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/ul[2]/li[3]/div/span[3]  //html/body/app-root/div/div/app-prov-ficha/div/div/div[1]/div[1]/div/div[2]/ul[2]/li[4]/div/span[3]
    [Teardown]  Fechar navegador e parar playwright
