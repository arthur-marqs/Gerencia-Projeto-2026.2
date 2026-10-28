# Backend do SetupFlow

Este guia explica como configurar o backend e o PostgreSQL em uma máquina de desenvolvimento.

Cada pessoa executa sua própria instância local do PostgreSQL. O GitHub contém as migrations que recriam a estrutura do banco, mas não contém o banco local, usuários de teste, sessões ou senhas.



## Ferramentas usadas

- Python 3.11
- PostgreSQL 18 (também usado no CI)
- FastAPI
- SQLAlchemy
- Alembic
- Psycopg 3

## Pré-requisitos

- Python instalado
- PostgreSQL instalado e em execução
- Git
- Windows PowerShell

## 1. Criar um usuário e um banco locais

Abra o PowerShell e conecte-se ao PostgreSQL com uma conta administradora:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres
```

No prompt do `psql`, crie o usuário da aplicação:

```sql
CREATE ROLE setupflow_dev
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;
```

Defina uma senha para esse usuário. O `psql` solicitará a senha sem exibi-la:

```text
\password setupflow_dev
```

Crie o banco de desenvolvimento:

```sql
CREATE DATABASE setupflow_dev
    OWNER setupflow_dev
    ENCODING 'UTF8';
```

Saia do `psql`:

```text
\q
```

A senha é local de cada desenvolvedor. Não a inclua em arquivos versionados nem a compartilhe no repositório.

## 2. Configurar o ambiente do backend

Na raiz do repositório, entre na pasta do backend e crie o ambiente virtual:

```powershell
Set-Location backend
py -3.11 -m venv .venv
```

Instale as dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crie seu arquivo local `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite `backend/.env` e informe a senha que você definiu para `setupflow_dev`. A configuração deve conter os parâmetros usados pelo backend, por exemplo:

```dotenv
DB_USER=setupflow_dev
DB_PASSWORD=sua_senha_local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=setupflow_dev
SESSION_TTL_HOURS=8
COOKIE_SECURE=false
```

O arquivo `.env` contém credenciais locais e não deve ser enviado ao Git. O arquivo `.env.example` deve conter apenas valores de exemplo.

## 3. Criar as tabelas

Com o ambiente configurado, aplique as migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

As migrations criam as tabelas, constraints e índices que declaram e inserem os perfis iniciais. Há um índice declarado no ORM que a migration inicial não cria; consulte o [documento do modelo de dados](../docs/arquitetura/modelo-de-dados.md) para essa diferença.

Para conferir a revisão aplicada:

```powershell
.\.venv\Scripts\alembic.exe current
```

Para conferir as tabelas, conecte-se ao banco da aplicação:

```powershell
psql -h localhost -p 5432 -U setupflow_dev -d setupflow_dev
```

No `psql`, liste as tabelas:

```text
\dt
```

As migrations também criam `produtos` e `maquinas`. O perfil `PLANEJADOR` pode cadastrar e consultar produtos em `/api/produtos` e máquinas em `/api/maquinas`; o perfil `OPERADOR` não tem acesso a essas rotas. Máquinas são cadastradas com código e nome obrigatórios, descrição opcional e status ativo por padrão.

Os testes de cadastro e controle de acesso das máquinas ficam em `testes/integration/test_us03_maquinas.py`. Configure `TEST_DATABASE_URL` como descrito acima e execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us03_maquinas.py
```
## 4. Criar um usuário local de teste

O banco começa sem usuários. Crie um usuário pelo script da aplicação:

```powershell
.\.venv\Scripts\python.exe -m scripts.create_initial_user
```

Siga as solicitações do script. A senha será armazenada como hash.

## 5. Iniciar o backend

Na pasta `backend`, execute:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app
```

Deixe o terminal aberto enquanto estiver usando a aplicação.

- Documentação da API: <http://127.0.0.1:8000/docs>
- Verificação de saúde: <http://127.0.0.1:8000/api/health>

Para encerrar o servidor, pressione `Ctrl+C`.

## 6. Iniciar o frontend

Abra outro terminal do PowerShell, volte à raiz do repositório e entre na pasta do frontend:

```powershell
Set-Location ..\frontend
npm install
npm run dev
```

Abra o endereço informado pelo Vite, normalmente <http://localhost:5173>.

O backend e o frontend precisam permanecer rodando em terminais separados.

## Testes de integração da US01

Os testes exercitam a API e um PostgreSQL real. Crie um banco exclusivo para testes com nome terminado em `_test`, por exemplo `setupflow_test`, usando uma conta administradora:

```sql
CREATE DATABASE setupflow_test
    OWNER setupflow_dev
    ENCODING 'UTF8';
```

Na pasta `backend`, configure `TEST_DATABASE_URL` no PowerShell com as credenciais locais do PostgreSQL:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://setupflow_dev:<SENHA>@localhost:5432/setupflow_test"
```

Se a senha tiver caracteres especiais, use a forma percent-encoded na URL. Os testes exigem essa variável e recusam a execução se o nome do banco não terminar em `_test`. Eles aplicam as migrations antes de limpar e preparar os dados isolados de cada caso. Não defina `DATABASE_URL` para executar a suíte; essa variável não é usada como fallback.

Instale as dependências do backend, incluindo pytest e httpx2 (usado pelo TestClient da versão atual do Starlette):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Execute a suíte básica de login e sessão:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us01_auth.py
```

Execute separadamente a suíte quantitativa do Driver05, que inclui 20 ciclos (200 solicitações bloqueadas) e valida isolamento e limites de tempo:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit-driver05.xml testes\integration\drivers\test_driver05_rate_limiting.py
```

As duas suítes também podem ser executadas juntas com `.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit.xml testes`.

## Desenvolvimento em equipe

Cada colega deve:

1. Criar seu próprio usuário PostgreSQL e banco local.
2. Criar seu arquivo `backend/.env` usando `.env.example` como referência.
3. Instalar as dependências.
4. Executar `alembic upgrade head`.
5. Criar seu próprio usuário de teste.

As migrations mantêm os esquemas dos bancos locais alinhados. Elas não compartilham os dados inseridos no banco de outra pessoa.