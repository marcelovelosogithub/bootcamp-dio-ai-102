# Task 5:

## **Tarefa 5: Sistema de validação com banco de dados.**

* [x] Criar uma função para inserir os dados validados em um bando de dados.
    
    * [x] Verificar se o número do cartão já existe no bd
    * [x] Se existir apenas informasr informar e não adicionar novamente.
    * [x] Caso não exista, validar as informações
    * [x] Adicionar um atributo `processed_at` com a data e hora em que o dado foi inserido
    * [x] Adicionar todos os dados no bd, exibir os resultados.

## Sistema de validação com banco de dados.

### Verificar se o número do cartão já existe no bd:

* **Na task 4 implementamos as funções:**
    * `upload_and_check_credit()`: Que envia a imagem ao blob storage e extrai as informações do cartão.
    * `display_credit_card_info()`: Que faz a validação e informa se o cartão é válido ou não.

* **Primeiro importar as libs e métodos:**


```python
from utils.Config import Config 
from services.blob_service import upload_to_blob
from services.credit_card_service import detect_credit_card_info
from services.data_base import DataBase 
import streamlit as st 
import datetime as dt
```

* **Instanciar o banco de dados:**


```python
# definir a pasta onde o banco será salvo: 
Config.DATABASE_PATH = "../data/credit.db"
```

```python
# Instanciar o banco
db = DataBase()
```

```python
# fazer upload e carregar as informações do cartão.
credit_card_info = upload_and_check_credit("../img/nubank.jpg") 
credit_valid = display_credit_card_info(credit_card_info)
```

    Cartão Válido
    Nome do Titular: GABRIEL LIMA
    Banco Emissor: ny
    bank
    Número do Cartão: 5032 9334 3764 9846
    Data de Expiração: 09/17


* **Primeiro vamos ajustar a função `display_credit_card_info()`:** 
    * Ela precisa retornar um dicionário pronto para adicionarmos ao banco de dados.


```python
def display_credit_card_info(credit_card_info): 
    # Verifica se as chaves existem, se não existirem retorna None
    issuing_bank = credit_card_info.get('IssuingBank')
    card_holder = credit_card_info.get('CardHolderName')
    card_number = credit_card_info.get('CardNumber')
    expiration_date = credit_card_info.get('ExpirationDate')
    # Verifica se todos os campos necessários estão presentes e não são None
    is_valid = all([issuing_bank, card_holder, card_number, expiration_date])
    #print(f"Cartão {'Válido' if is_valid else 'Inválido'}")    
    card_info = {
        "card_name": credit_card_info.get('CardHolderName', 'Não detectado'),
        "card_number": card_number,
        "expiry_date": credit_card_info.get('ExpirationDate', 'Não detectado'),
        "bank_name": credit_card_info.get('IssuingBank', 'Não detectado'),
        "is_valid":"true" if all([
            credit_card_info.get('IssuingBank'),
            credit_card_info.get('CardHolderName'),
            credit_card_info.get('CardNumber'),
            credit_card_info.get('ExpirationDate')
        ]) else "false",
        "processed_at": str(dt.datetime.now())
    }
    return card_info, is_valid
```

* **Vamos testar a função agora:**


```python
card_information, card_valid = display_credit_card_info(credit_card_info)
print(f"Cartão:{card_valid}") 
print(f"informação do cartão: {card_information}")
```

    Cartão:True
    informação do cartão: {'card_name': 'GABRIEL LIMA', 'card_number': '5032 9334 3764 9846', 'expiry_date': '09/17', 'bank_name': 'ny\nbank', 'is_valid': 'true', 'processed_at': '2024-11-13 21:57:47.082183'}


* **Perfeito agora temos a validação e os resultados no formato correto para adicionar ao banco de dados.**

* **Salvando no banco de dados:**


```python
# Verifica se existe número do cartão antes de tentar salvar
card_number = credit_card_info.get('CardNumber')
if not card_number:
    print("Número não do cartão não encontrado. Os dados não serão salvos.")
# Verificar se o número existe do banco de dados
existing_card = db.get_card_by_number(card_number)
if existing_card:
    print(f"o cartão com o número {card_number} já existe do banco de dados")
elif credit_valid:
    db.insert_card(card_info)
    print("Informações do cartão salvas no banco de dados!")
else: 
    print("Os dados não foram salvos no banco de dados!")
card_info
```

    Informações do cartão salvas no banco de dados!

    {'card_name': 'GABRIEL LIMA',
     'card_number': '5032 9334 3764 9846',
     'expiry_date': '09/17',
     'bank_name': 'ny\nbank',
     'is_valid': 'true',
     'processed_at': '2024-11-13 21:34:58.304212'}

* **Tudo certo, cartão validado e inserido no banco, vamos conferir se realmente foram salvos.**


```python
# módulo para trazer todas as informações do banco 
db.get_all_cards() 
```

    [{'id': 1,
      'card_name': 'GABRIEL LIMA',
      'card_number': '5032 9334 3764 9846',
      'expiry_date': '09/17',
      'bank_name': 'ny\nbank',
      'is_valid': 'true',
      'processed_at': '2024-11-13 21:34:58.304212'}]


* **Agora conseguimos salvar as informações!**.
* **Nesse caso como se trata de uma POC e essas informações não são reais não estamos realizando nenhum tratamento visando a segurança das informação etc...**.

* **Encapsulando tudo em uma função para depois implementar no frontend:** 


```python
def save_card_info(credit_info, credit_valid):
    db = DataBase()
    # Verifica se existe número do cartão antes de tentar salvar
    card_number = credit_card_info.get('CardNumber')
    if not card_number:
        print("Número não do cartão não encontrado. Os dados não serão salvos.")
    # Verificar se o número existe do banco de dados
    existing_card = db.get_card_by_number(card_number)
    if existing_card:
        print(f"o cartão com o número {card_number} já existe do banco de dados")
    elif credit_valid:
        db.insert_card(card_info)
        print("Informações do cartão salvas no banco de dados!")
    else: 
        print("Os dados não foram salvos no banco de dados!")
    return card_info
```

* **Bora testar:**


```python
credit_info, card_valid = display_credit_card_info(credit_card_info)
save_card_info(credit_info, card_valid)
```

    o cartão com o número 5032 9334 3764 9846 já existe do banco de dados

    {'card_name': 'GABRIEL LIMA',
     'card_number': '5032 9334 3764 9846',
     'expiry_date': '09/17',
     'bank_name': 'ny\nbank',
     'is_valid': 'true',
     'processed_at': '2024-11-13 21:34:58.304212'}



* **Legal como esse número de cartão já existe ele não foi adicionado.**

