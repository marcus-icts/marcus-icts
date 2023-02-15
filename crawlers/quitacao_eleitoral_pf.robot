*** Settings ***
Library  ../core/robot-libs/CoreLib.py


*** Variables ***
${URL_TSE}                                  https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-quitacao-eleitoral
${CAMPO_NOME_ELEITOR}                       //*[@id="QE_NomeEleitor"]
${CAMPO_TITULO_OU_CPF}                      //*[@id="QE_NumeroTituloCPF"]
${CAMPO_DATA_NASCIMENTO}                    //*[@id="QE_DataNascimento"]
${CAMPO_MAE}                                //*[@id="QE_NomeMae"]
${CAMPO_NAO_CONSTA_MAE}                     //*[@id="QE_NaoConstaMae"]
${CAMPO_PAI}                                //*[@id="QE_NomePai"]
${CAMPO_NAO_CONSTA_PAI}                     //*[@id="QE_NaoConstaPai"]
${BTN_EMITIR}                               //*[@id="form-quitacao-eleitoral"]/fieldset/button


*** Tasks ***
Buscar quitação eleitoral
    quitacao eleitoral                                       ${nome}    ${cpf_titulo}    ${data_nascimento}    ${nome_mae}    ${nome_pai}
    [Teardown]  Fechar navegador e parar playwright
