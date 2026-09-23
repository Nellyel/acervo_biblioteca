# Acervo Biblioteca

Projeto desenvolvido em Django para a disciplina de Laboratório de Programação Full Stack.

O sistema permite cadastrar, listar e pesquisar livros de um acervo bibliográfico.

## Funcionalidades atuais

- Cadastro de livros
- Listagem do acervo
- Tipo de acervo: Digital ou Físico
- Categorias bibliográficas de 000 a 900
- Pesquisa por nome, tipo e categoria

## Instalação

Crie e ative um ambiente virtual:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

## Execução

Aplique as migrações do banco de dados:

```powershell
python manage.py migrate
```

Inicie o servidor:

```powershell
python manage.py runserver
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8000/livros/
```

## Tecnologias utilizadas

- Python 3.12
- Django
- HTML
- SQLite
- Git e GitHub