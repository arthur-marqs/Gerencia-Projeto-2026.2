# Backend do SetupFlow

Este guia explica como configurar o backend e o PostgreSQL em uma máquina de desenvolvimento.

Cada pessoa executa sua própria instância local do PostgreSQL. O GitHub contém as migrations que recriam a estrutura do banco, mas não contém o banco local, usuários de teste, sessões ou senhas.



## Ferramentas usadas

- Python 3.11
- PostgreSQL 18.6
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

As migrations criam as tabelas de autenticação, os índices e os perfis iniciais definidos no projeto.

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

**Obs: Nesta US01 foram implementadas apeans as seguintes tabelas: controle_tentativas_login, falhas de_login, perfis, usuarios, usuario_perfil e sessoes.**                                                   
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

## Banco para testes automatizados

Quando os testes automatizados forem configurados, use um banco separado, como `setupflow_test`. Não execute testes em um banco com dados que você queira preservar.

A configuração dos testes deve selecionar o banco `setupflow_test`, aplicar as migrations nele e limpar os dados entre os testes. Nunca use credenciais reais em testes ou no repositório.

## Desenvolvimento em equipe

Cada colega deve:

1. Criar seu próprio usuário PostgreSQL e banco local.
2. Criar seu arquivo `backend/.env` usando `.env.example` como referência.
3. Instalar as dependências.
4. Executar `alembic upgrade head`.
5. Criar seu próprio usuário de teste.

As migrations mantêm os esquemas dos bancos locais alinhados. Elas não compartilham os dados inseridos no banco de outra pessoa.