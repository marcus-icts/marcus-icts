# ICTS Crawler (subject to change, WIP)

## Requisitos
	- Python 3.9.1 ou superior;
## Instalação
sudo  apt install python3.<version>-venv
python -m venv venv
source ./venv/bin/activate

```sh
(venv) $ pip install -r requirements.txt
(venv) $ python -m playwright install
```
## Configuração

A configuração da aplicação é feita através de variáveis de ambiente. Verificar as variáveis disponíveis no arquivo *.env-example*. As variáveis de ambiente podem ser configurados em um arquivo *.env* na raiz do projeto.

## Execução
### Execução simples
Caso queira rodar o crawler diretamente - para testes e afins - basta executar o comando como nos exemplos abaixo:
```sh
(venv) $ python main.py run --subject compras_publicas_ecuador --related-data '{"razao_social": "lexim"}'
(venv) $ python main.py run --subject comprasal_lista_provedores --related-data '{"name": "juan carlos"}'

(venv) $ python main.py run -s compras_publicas_equador -d '{"razao_social": "lexim"}'
(venv) $ python main.py run -s perfil_prov -d '{"ruc": "J Y S CONTRATISTAS GENERALES Y PROVEEDORES S.R.L."}'
```
Onde *subject* é o nome do script do Robot (sem a exntesão .robot) e *related-data* são os dados necessários para realizar a busca.

### Consumidor
Para subir o consumidor do crawler basta executar o comando abaixo:

```sh
(venv) $ python main.py consume
```

## Desenvolvimento
Para se criar um novo crawler um script do Robot deve ser criado dentro da pasta *crawlers*. A biblioteca **CoreLib** oferece diversas palavras chaves para auxiliar no desenvolvimento de novos crawlers. A documentação das palavras chaves pode ser encontrada em *docs/CoreLib.html*.
