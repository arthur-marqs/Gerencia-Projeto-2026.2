# Aceite BDD da US-32

A suíte utiliza Cypress 16 + Cucumber/Gherkin em português, API FastAPI real e
PostgreSQL. Os 12 critérios da US-32 são rastreados por `@CT32` a `@CT43`, com
32 execuções após expandir os Exemplos. O smoke é um subconjunto de 5 execuções.

## Ambiente local

Use um banco **exclusivo** terminado em `_e2e_test`, por exemplo
`setupflow_e2e_test`. Ele será limpo antes de **cada** cenário. O banco usado
por Pytest e o banco de desenvolvimento/demonstração devem ser diferentes.

No PostgreSQL, com uma conta autorizada a criar bancos, prepare:

```sql
CREATE DATABASE setupflow_e2e_test OWNER setupflow_dev ENCODING 'UTF8';
```

No primeiro PowerShell, na raiz do repositório, configure as credenciais locais
sem incluí-las nas evidências. Informe uma URL SQLAlchemy válida, com a senha
percent-encoded se contiver caracteres especiais:

```powershell
$env:DB_USER = 'setupflow_dev'
$env:DB_PASSWORD = Read-Host 'Senha local do PostgreSQL'
$env:DB_HOST = 'localhost'
$env:DB_PORT = '5432'
$env:DB_NAME = 'setupflow_e2e_test'
$env:COOKIE_SECURE = 'false'
$env:E2E_DATABASE_URL = Read-Host 'URL PostgreSQL do banco E2E (postgresql+psycopg://...)'
Set-Location backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

No segundo terminal, a partir da raiz:

```powershell
Set-Location frontend
npm ci
npx cypress install
npm run build
npm run preview -- --host 0.0.0.0 --port 5173
```

No terceiro terminal, a partir da raiz, informe a **mesma URL E2E** usada pelo
backend. As variáveis `DB_*` também são necessárias para executar o script inicial
no cenário de instalação, pois a configuração da aplicação é validada no import.

```powershell
$env:DB_USER = 'setupflow_dev'
$env:DB_PASSWORD = Read-Host 'Senha local do PostgreSQL'
$env:DB_HOST = 'localhost'
$env:DB_PORT = '5432'
$env:DB_NAME = 'setupflow_e2e_test'
$env:E2E_DATABASE_URL = Read-Host 'URL PostgreSQL do banco E2E (postgresql+psycopg://...)'
$env:E2E_PYTHON = (Resolve-Path backend/.venv/Scripts/python.exe).Path
Set-Location frontend
npm run test:e2e:smoke -- --browser chrome
npm run test:e2e:regressao -- --browser chrome
npm run test:e2e:regressao -- --browser electron
```

Execute os navegadores sequencialmente quando compartilham o banco local. No
CI, cada navegador roda em outro job, com seu próprio serviço PostgreSQL.
Para o modo interativo, use `npm run test:e2e:open` no mesmo ambiente. O terminal
não deve definir `ELECTRON_RUN_AS_NODE` para iniciar o aplicativo interativo.

## Como a preparação funciona

`cypress.config.cjs` registra tasks Node que executam `scripts.seed_e2e`, sem
expor endpoints de teste na API. O script só abre conexão para um PostgreSQL
cujo nome termine em `_e2e_test`. Há seis testes unitários verificando a recusa
antes de qualquer conexão para configurações inválidas ou bancos indevidos.

As fixtures geram usuários fictícios com perfis Administrador/Planejador/Operador,
conta inativa, conta sem vínculos e autores de ordem e planejamento. A senha
fictícia da suíte é definida em `seed_e2e.py` e nos steps. Senhas são digitadas
com `log: false`; os tasks de autenticação não registram cookies nos relatórios.

O CT43 começa sem contas e chama o script inicial com entradas controladas;
depois verifica o login do administrador e o cadastro de outra conta pela tela.
Os demais cenários também são independentes e podem ser executados isoladamente.

Quando o Python está em um contêiner já configurado para esse banco, é possível
usar `E2E_SEED_CONTAINER=<nome>` em vez de `E2E_PYTHON`. O contêiner deve ter o
repositório montado, dependências instaladas, diretório de trabalho `backend` e
as variáveis `DB_*`/`E2E_DATABASE_URL` corretas. Não é necessário para executar no CI.

## Tags e comandos

| Comando | Seleção |
| --- | --- |
| `npm run test:e2e:smoke -- --browser chrome` | `@smoke and not @wip` |
| `npm run test:e2e:regressao -- --browser electron` | `@regressao and not @wip` |
| `npm run test:e2e -- --browser chrome --tags "@CT39"` | Somente bloqueios por vínculos |
| `npm run test:e2e:open` | Interface interativa do Cypress |

O runner passa as tags para `config.expose`, usado pelo preprocessor no Cypress 16.
Credenciais e URL do banco não são copiadas para `expose`.

## Evidências

Os comandos geram `frontend/artifacts/cypress/<navegador>/<smoke|regressao>/`:

- `run-summary.json`: data UTC, branch/commit, alterações locais, hash das fontes,
  ambiente, versões, duração e status de cada cenário.
- `cucumber-report.json` e `cucumber-report.html`: resultado Gherkin e anexos.
- `junit/results-*.xml`: resultado para ferramentas de CI.
- `screenshots/`: uma captura por cenário, capturas intermediárias relevantes e
  captura automática de falhas.
- `videos/`: gravação da spec executada, inclusive quando houver falha.

`E2E_ARTIFACTS_DIR` permite definir outra pasta de saída. No GitHub Actions,
o job publica esses arquivos em `us32-bdd-chrome` e `us32-bdd-electron`, mesmo
quando os testes falham. A regressão inclui os cinco casos smoke.

O runner retorna erro se o Cypress falhar, houver teste reprovado ou nenhum teste
for selecionado. Os relatórios locais não afirmam que houve execução remota do CI.
Os artefatos completos são ignorados pelo Git. Os relatórios e prints selecionados
desta entrega estão no [registro de evidências da US-32](../../docs/releases/release2/sprint2/evidencias/us32/README.md).

## Referências de configuração

- [Preprocessor Cucumber — configuração oficial](https://github.com/badeball/cypress-cucumber-preprocessor/blob/master/docs/quick-start.md).
- [Cypress — execução em GitHub Actions](https://docs.cypress.io/app/continuous-integration/github-actions).
- [Plano de testes original](../../docs/qualidade/Plano-de-Teste-SetupFlow.docx).
