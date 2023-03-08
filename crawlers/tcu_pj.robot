*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Tasks ***
Buscar em TCU PJ
    Abrir o navegador em                                                    https://contas.tcu.gov.br/certidao/Web/Certidao/NadaConsta/home.faces
    Resolver TCU recaptchaV2                                                https://contas.tcu.gov.br/certidao/Web/Certidao/NadaConsta/home.faces   6LcRIUAkAAAAAGWdjhHC8mn-5A87StjjSVkn9N54
    Clicar em                                                               //*[@id="formEmitirCertidaoNadaConsta:tipoPesquisa:1"]
    Digitar Texto Em Campo                                                  ${cnpj}  //*[@id="formEmitirCertidaoNadaConsta:txtCpfOuCnpj"]
    Clicar em                                                               //*[@id="formEmitirCertidaoNadaConsta:btnEmitirCertidao"]
    Esperar                                                                 10
    Extrair span TCU
    [Teardown]  Fechar navegador e parar playwright
