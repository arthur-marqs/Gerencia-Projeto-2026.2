# Aceite BDD das US11, US13, US14 e US32

A suíte utiliza Cypress 16 + Cucumber/Gherkin em português, API FastAPI real e PostgreSQL exclusivo para testes.

A US32 cobre o gerenciamento de usuários, com os casos `@CT32` a `@CT43`. A US11 cobre a consulta da matriz de setup e a regressão de famílias ausentes. A US13 automatiza os 13 casos de geração e consulta da sequência sugerida em [`sugestao.feature`](e2e/sugestao.feature).

A US14 automatiza seis execuções de sequenciamento por prazos e prioridades
em [`prazos-prioridades.feature`](e2e/prazos-prioridades.feature).

O smoke usa `@smoke` e a regressão usa `@regressao`. Na US13, o smoke inclui o CT-107 e o CT-110.

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

Para a US11, os modos `matriz` e `matriz-vazia` preparam duas famílias fictícias (`FAM-A` e `FAM-B`). O modo `matriz` cadastra tempos direcionais de 30 minutos de A para B e 75 minutos de B para A. O modo `matriz-vazia` mantém as famílias, mas não cadastra tempos de setup.

Cada funcionalidade prepara seus dados em um hook restrito à tag da US correspondente.

### Cenários da US13

O modo `sugestao` prepara usuários, famílias A e B e as ordens OP01 a OP05 em um banco reiniciado por cenário. Os steps cadastram os tempos direcionais necessários pela API real. O task `e2e:inspecionar-sugestoes` lê as contagens de sugestões e itens no banco isolado para verificar que uma falha de validação não grava registros parciais.

| Tags | Cobertura |
| --- | --- |
| `@CT79`, `@CT80`, `@CT81` | Redução de setup, ordem única e resultado restrito aos IDs selecionados |
| `@CT82`, `@CT83`, `@CT84` | Produto sem família, sentido de troca ausente e nova tentativa após corrigir os dados |
| `@CT85` | Negação de acesso ao Operador pela API e preservação da sugestão e do planejamento existentes |
| `@CT107`, `@CT108`, `@CT109` | Geração antes de salvar o manual, preservação da sequência de menor custo e empate |
| `@CT110`, `@CT111`, `@CT112` | Recuperação após recarregar, seleção vazia e várias ordens da mesma família |

O CT-119 depende da integração com a US15.

### Cenários da US14

A US14 utiliza o modo `sugestao` para preparar os dados de teste,
reaproveitando as fixtures e os steps da US13.

Os cenários verificam o sequenciamento considerando prazos, prioridades,
durações estimadas e tempos de setup, utilizando a API e o banco de testes.

| Caso | Cobertura |
| --- | --- |
| US14_CT01 | Priorização de ordem urgente mesmo com aumento de setup |
| US14_CT02 | Prazo mais próximo antes do setup menor em ordens de mesma prioridade |
| US14_CT03 | Prioridades diferentes em ordens de mesmo prazo |
| US14_CT04 | Bloqueio da geração com dados de planejamento incompletos |
| CT-115 (`@US14_CT05`, `@CT115`) | Prazo restritivo antecipa Baixa sem atrasar Alta. Com ambos os prazos viáveis, Alta vem primeiro |

A tag `@US14` seleciona todos os casos da história. A tag `@CT115`
seleciona os dois exemplos de conflito.

### Cenários da US32

O CT43 começa sem contas e chama o script inicial com entradas controladas;
depois verifica o login do administrador e o cadastro de outra conta pela tela.
Os demais cenários também são independentes e podem ser executados isoladamente.

### Execução com contêiner

Quando o Python está em um contêiner já configurado para esse banco, é possível
usar `E2E_SEED_CONTAINER=<nome>` em vez de `E2E_PYTHON`. O contêiner deve ter o
repositório montado, dependências instaladas, diretório de trabalho `backend` e
as variáveis `DB_*`/`E2E_DATABASE_URL` corretas. Não é necessário para executar no CI.

## Tags e comandos

`cypress.config.cjs` descobre as features de aceite em `cypress/e2e/*.feature` e executa os cenários das US11, US13, US14 e US32 filtrados pelas tags, com API e banco reais. `cypress.config.ts` executa os cenários de autenticação.


| Comando | Seleção |
| --- | --- |
| `npm run test:e2e:smoke -- --browser chrome` | `@smoke and not @wip` |
| `npm run test:e2e:regressao -- --browser electron` | `@regressao and not @wip` |
| `npm run test:e2e -- --browser chrome --tags "@US13 and not @wip"` | Os 13 casos da sequência sugerida |
| `npm run test:e2e -- --browser chrome --tags "@US14 and not @wip"` | Os seis casos de prazos e prioridades |
| `npm run test:e2e -- --browser chrome --tags "@CT110"` | Recuperação da sugestão e preservação do planejamento manual |
| `npm run test:e2e -- --browser chrome --tags "@CT39"` | Somente bloqueios por vínculos |
| `npm run test:e2e:open` | Interface interativa do Cypress |
| `npm run test:e2e:login -- --browser chrome` | Validação de login, sem preparação do banco E2E |

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

No GitHub Actions, a regressão BDD inclui a feature da US14 em Chrome
e Electron pela tag `@regressao`. Os jobs publicam os relatórios e capturas nos artefatos `acceptance-bdd-chrome` e `acceptance-bdd-electron`, inclusive em caso de falha. As capturas da US13 usam os IDs dos casos do plano. O CT-85 é verificado pela API e consta nos relatórios.

O runner retorna erro se o Cypress falhar, houver teste reprovado ou nenhum teste
for selecionado. Os relatórios locais não afirmam que houve execução remota do CI.
Os artefatos completos são ignorados pelo Git. Os relatórios e prints selecionados
desta entrega estão no [registro de evidências da US-32](../../docs/releases/release2/sprint2/evidencias/us32/README.md).

Os resultados locais da US14 e da regressão completa no Chrome estão
documentados no [relatório de testes da US14](../../docs/releases/release2/sprint3/relatorio-testes-us14.md),
com os relatórios JUnit, resumos de execução e capturas dos quatro cenários.

## Referências de configuração

- [Preprocessor Cucumber — configuração oficial](https://github.com/badeball/cypress-cucumber-preprocessor/blob/master/docs/quick-start.md).
- [Cypress — execução em GitHub Actions](https://docs.cypress.io/app/continuous-integration/github-actions).
- [Plano de testes original](../../docs/qualidade/Plano-de-Teste-SetupFlow.docx).
