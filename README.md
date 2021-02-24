# Project Zeta (subject to change)

## Requisitos
	- Python 3.9.1 ou superior;
## Instalação
É recomendado realizar a instalação em um ambiente virtual isolado ([virtualenv](https://docs.python.org/3/library/venv.html)). Para instalar as dependências do projeto executar os seguintes comandos dentro da pasta raiz do projeto:

```sh
$ pip install -r requirements.txt
$ python -m playwright install
```
## Configuração

A configuração da aplicação é feita através de variáveis de ambiente. Verificar as variáveis disponíveis no arquivo *.env-example*. As variáveis de ambiente podem ser configurados em um arquivo *.env* na raiz do projeto.

## Execução
Para executar uma instância do crawler basta executar o comando na pasta raiz do projeto:

```sh
$ python main.py
```
