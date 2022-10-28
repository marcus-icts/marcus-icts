*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TCU PF
    Abrir o navegador em                                                    https://contas.tcu.gov.br/certidao/Web/Certidao/NadaConsta/home.faces    false  3000
    Clicar em                                                               //*[@id="formEmitirCertidaoNadaConsta:tipoPesquisa:0"]
    Digitar Texto Em Campo                                                  ${cpf}  //*[@id="formEmitirCertidaoNadaConsta:txtCpfOuCnpj"]
    Clicar em                                                               //*[@id="formEmitirCertidaoNadaConsta:btnEmitirCertidao"]
    Esperar                                                                 10
    Extrair span TCU
    [Teardown]  Fechar navegador e parar playwright
