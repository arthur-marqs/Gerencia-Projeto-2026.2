# Testes automatizados da US01

Os testes exercitam a API real e um PostgreSQL real. Eles cobrem login válido, credenciais inválidas, validação do corpo, criação da sessão, consulta da sessão em `/api/auth/me`, retorno de identidade e perfis, rejeição de sessão expirada e logout.

## Testes quantitativos do Driver05

Os cenários de limitação de tentativas ficam separados da suíte básica em `testes/integration/drivers/test_driver05_rate_limiting.py`. A suíte parametriza 20 ciclos: em cada ciclo, cinco falhas acionam o bloqueio e dez solicitações seguintes (incluindo uma com senha correta) são rejeitadas sem criar sessão. As requisições são alternadas entre duas instâncias FastAPI de teste que compartilham o mesmo PostgreSQL. Cada ciclo também valida uma conta diferente com credenciais válidas. Testes adicionais controlam o relógio da aplicação para conferir o limite exato de 15 minutos e ajustam timestamps no banco de teste para validar a janela móvel de cinco minutos.

Execute o Driver05 separadamente:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit-driver05.xml testes\integration\drivers\test_driver05_rate_limiting.py
```

O resultado esperado é 20 ciclos aprovados, 200 solicitações bloqueadas sem sessões, 20 autenticações válidas de outras contas sem bloqueio indevido e aprovação dos testes de fronteira temporal. A suíte requer o mesmo `TEST_DATABASE_URL` seguro descrito acima.

## Segurança do banco de teste

Os testes limpam as tabelas de autenticação antes de cada caso. Use um banco separado cujo nome termine em `_test`, por exemplo `setupflow_test`. Não use `setupflow_dev` nem um banco com dados que queira preservar.

Crie o banco exclusivo uma vez no PostgreSQL, usando seu usuário administrador:

```sql
CREATE DATABASE setupflow_test OWNER setupflow_dev ENCODING 'UTF8';
```

## Executar no PowerShell

No diretório `backend`, configure `TEST_DATABASE_URL` com as credenciais do seu ambiente. Substitua `<SENHA>` pela senha local do usuário PostgreSQL e use percent-encoding se ela contiver caracteres especiais:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://setupflow_dev:<SENHA>@localhost:5432/setupflow_test"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us01_auth.py
```

O fixture exige `TEST_DATABASE_URL`, valida o PostgreSQL e recusa bancos cujo nome não termine em `_test` antes de aplicar migrations ou limpar dados. A suíte não usa `DATABASE_URL` como fallback.

## Contrato esperado

O teste segue o contrato observado na implementação da API: `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`, campos `email` e `password`, resposta `usuario` com `id`, `nome`, `email` e `perfis`, cookie `setupflow_session` e tabelas PostgreSQL em português. Os testes quantitativos do Driver05 permanecem em uma suíte separada.
