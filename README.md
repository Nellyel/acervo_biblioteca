# Acervo Biblioteca

Projeto desenvolvido para a disciplina de Laboratório de
Programação Full Stack, utilizando Django e Django REST Framework.

O sistema permite gerenciar acervos bibliográficos de diferentes
organizações, com controle de acesso, empréstimos, reservas,
indicadores e integração por API REST.

## Funcionalidades

### Gestão do acervo

- Cadastro, listagem e pesquisa de livros.
- Cadastro de autores, exemplares e membros.
- Classificação do acervo em Digital ou Físico.
- Categorias bibliográficas de 000 a 900.
- Pesquisa por nome, tipo e categoria.

### Empréstimos e reservas

- Registro de empréstimos e devoluções.
- Controle automático da disponibilidade dos exemplares.
- Cálculo de dias de atraso.
- Multa de R$ 1,00 por dia de atraso.
- Fila de reservas com atualização automática de posição.

### Multi-organização e segurança

- Cadastro de organizações.
- Perfis vinculados a organizações.
- Isolamento de dados entre bibliotecas nas páginas e na API.
- Autenticação de usuários.
- Controle de acesso por papel:
  - Administrador: consulta e gerenciamento pela API.
  - Operador: consulta pela API.
- Proteção das operações administrativas.

### Dashboard

- Total de empréstimos.
- Empréstimos abertos e devolvidos.
- Ranking dos cinco livros mais emprestados.
- Filtro por período.
- Gráfico de empréstimos por mês.
- Exportação de empréstimos em CSV.
- Gráfico e exportação exclusivos para administradores.

## API REST

A API utiliza Django REST Framework, autenticação,
permissões por papel e isolamento por organização.

| Recurso | Endpoint |
|---|---|
| Livros | /api/livros/ |
| Autores | /api/autores/ |
| Exemplares | /api/exemplares/ |
| Membros | /api/membros/ |
| Empréstimos | /api/emprestimos/ |
| Reservas | /api/reservas/ |

Os recursos disponibilizam operações de CRUD,
respeitando as permissões e regras de negócio.

Métodos HTTP disponíveis:

- GET: consultar registros.
- POST: cadastrar registros.
- PUT: atualizar registros.
- PATCH: atualizar parcialmente.
- DELETE: excluir registros.

Para acessar um registro individual, acrescente seu ID
ao endpoint correspondente.

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

Aplique as migrações:

```powershell
python manage.py migrate
```

Crie um superusuário:

```powershell
python manage.py createsuperuser
```

Inicie o servidor:

```powershell
python manage.py runserver
```

No painel administrativo, cadastre uma organização,
um usuário e seu respectivo perfil.

## Rotas principais

| Página | Endereço |
|---|---|
| Administração | /admin/ |
| Listagem de livros | /livros/ |
| Cadastro de livros | /livros/novo/ |
| Dashboard | /dashboard/ |
| Exportação CSV | /dashboard/csv/ |

Servidor local: http://127.0.0.1:8000/

## Testes automatizados

Execute:

```powershell
python manage.py test
```

O projeto possui nove testes automatizados que contemplam:

- Bloqueio de usuários não autenticados.
- Bloqueio de usuários sem perfil.
- Isolamento entre organizações na API de livros.
- Permissões por papel.
- Validação do ano de publicação.
- Disponibilidade dos exemplares.
- Cálculo de multas.
- Fila de reservas.
- Operações e permissões dos novos endpoints REST.

Verificação geral do projeto:

```powershell
python manage.py check
```

## Tecnologias utilizadas

- Python 3.12
- Django
- Django REST Framework
- SQLite
- HTML
- JavaScript
- Chart.js
- Git e GitHub

## Desenvolvimento

Projeto acadêmico desenvolvido durante as etapas P1 e P2
da disciplina de Laboratório de Programação Full Stack.