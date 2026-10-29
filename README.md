# SetupFlow

Sistema web para apoiar o planejamento e o acompanhamento da produção em pequenas e médias indústrias.

## Sobre o projeto

O SetupFlow busca auxiliar pequenas e médias indústrias no planejamento da sequência de produção.

O projeto está em desenvolvimento. A versão atual implementa autenticação, controle de acesso e funcionalidades de cadastro; a geração automática de sequências de produção ainda não está disponível.

## Equipe

- Arthur de Souza Marques
- Leonardo Istamilo Silva Ferreira
- Luiz Inácio Moura da Costa

## Papéis — Release 1

- **Product Owner (PO):** Leonardo
- **Scrum Master (SM):** Arthur Marques
- **Quality Assurance (QA):** Luiz Inácio Moura da Costa
- **DevOps:** Leonardo

## Responsabilidades

### Product Owner (PO)

- Organizar e priorizar o Product Backlog;
- definir e revisar as User Stories e seus critérios de aceite;
- preencher e conferir a Definition of Ready (DoR) das User Stories antes da Sprint Planning;
- esclarecer dúvidas sobre requisitos e regras de negócio;
- conferir a Definition of Done (DoD) dos itens entregues durante a Sprint Review;
- aceitar ou rejeitar os itens entregues.

### Scrum Master (SM)

- Acompanhar o andamento das sprints;
- auxiliar na organização das cerimônias do Scrum;
- registrar e acompanhar impedimentos;
- acompanhar a atualização do plano de riscos;
- apoiar a equipe no cumprimento do processo definido.

### Quality Assurance (QA)

- Elaborar e atualizar o plano de qualidade;
- elaborar um plano de teste para cada sprint;
- verificar se os testes das funcionalidades implementadas foram criados e executados;
- acompanhar a execução dos testes definidos para a sprint;
- registrar e acompanhar bugs quando encontrados;
- verificar os critérios de aceite e a Definition of Done;
- acompanhar as métricas de qualidade definidas pela equipe.

### DevOps

- Organizar e manter a estrutura do repositório;
- configurar e manter o pipeline de integração contínua;
- apoiar a configuração dos ambientes do projeto;
- acompanhar builds, testes e deploys;
- garantir que os testes sejam executados no pipeline quando aplicável.

## Tecnologias

- **Frontend:** React, TypeScript, Vite e Tailwind CSS
- **Backend:** Python 3.11, FastAPI e SQLAlchemy
- **Banco de dados:** PostgreSQL 18
- **Migrações:** Alembic
- **Testes:** Pytest, TestClient e PostgreSQL
- **CI:** GitHub Actions

## Como executar localmente

Pré-requisitos: Windows com PowerShell, Python 3.11, Node.js 22 e PostgreSQL 18. O frontend usa Vite 8; consulte os requisitos atuais de Node.js no [guia do frontend](frontend/README.md).

Configure o PostgreSQL, crie o banco local, configure `backend/.env` e aplique as migrations seguindo o [guia de configuração do backend](backend/README.md). Não versione o `.env` nem compartilhe suas credenciais.

Instale as dependências do frontend na primeira execução:

```powershell
Set-Location .\frontend
npm ci
```

Inicie o backend em um terminal PowerShell:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Em outro terminal, inicie o frontend:

```powershell
Set-Location .\frontend
npm run dev
```

Abra o endereço exibido pelo Vite, normalmente <http://localhost:5173>. A API e sua documentação interativa ficam em <http://127.0.0.1:8000> e <http://127.0.0.1:8000/docs>; a verificação de saúde está em <http://127.0.0.1:8000/api/health>.

## Como testar

### Backend

Os testes de integração usam PostgreSQL real. Crie e use um banco exclusivo para testes, com nome terminado em `_test` (por exemplo, `setupflow_test`), seguindo o [guia de testes do backend](backend/README.md). Na pasta `backend`, configure `TEST_DATABASE_URL` para esse banco e execute a suíte:

```powershell
Set-Location .\backend
$env:TEST_DATABASE_URL = "postgresql+psycopg://setupflow_dev:<SENHA>@localhost:5432/setupflow_test"
.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit.xml testes
```

Não execute a suíte usando o banco de desenvolvimento. O fixture valida que `TEST_DATABASE_URL` aponta para PostgreSQL e que o nome termina em `_test`. O comando grava o relatório JUnit em `backend/junit.xml`.

Para executar apenas uma suíte, informe o arquivo de teste, por exemplo:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us03_maquinas.py
```

### Frontend

Na pasta `frontend`, execute as verificações de lint e compilação de produção:

```powershell
Set-Location .\frontend
npm run lint
npm run build
```

O GitHub Actions executa os testes do backend e as verificações de lint e build do frontend em pushes e pull requests.

## Funcionalidades implementadas

- **Autenticação e sessão (US01):** login integrado à API, senha armazenada como hash, sessão persistida no PostgreSQL, consulta da identidade autenticada e logout.
- **Proteção contra tentativas repetidas (Driver05):** registro de falhas de login e bloqueio temporário após tentativas inválidas consecutivas.
- **Controle de acesso por perfil (US02):** operações de cadastro são restritas ao perfil Planejador de Produção; o perfil Operador não acessa recursos exclusivos do Planejador.
- **Gerenciamento de máquinas (US03):** cadastro, consulta, edição, ativação, inativação e exclusão quando não há registros vinculados. A tela e a API aplicam as permissões por perfil.
- **Produtos e famílias (US04–US06):** cadastro e consulta de produtos e famílias, com associação e remoção da associação entre produto e família.
- **Ordens de produção (US07–US08):** cadastro e consulta de ordens, além da definição e atualização de prazo e prioridade.
- **Interface web:** telas de login, máquinas, produtos, famílias e ordens de produção conectadas à API.


## Documentação

Consulte o [guia do backend](backend/README.md) para detalhes de configuração do PostgreSQL e execução da API, o [guia do frontend](frontend/README.md) para requisitos e execução da interface e o [mapa visual do projeto](docs/estrutura-projeto.md) para conhecer a estrutura atual do repositório.
---
## Organização arquitetural planejada (referência futura)

O SetupFlow utiliza um único repositório para backend, frontend, testes e documentação. A árvore abaixo é uma proposta de organização futura, não um inventário do código implementado. Para a estrutura atual, consulte o [mapa visual do projeto](docs/estrutura-projeto.md).

```text
setupflow/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── user-story.md
│   │   └── bug_report.md
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── machines.py
│   │   │       ├── families.py
│   │   │       ├── products.py
│   │   │       └── production_orders.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── permissions.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── auth_session.py
│   │   │   ├── login_attempt.py
│   │   │   ├── idempotency_record.py
│   │   │   ├── machine.py
│   │   │   ├── family.py
│   │   │   ├── product.py
│   │   │   └── production_order.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── machine.py
│   │   │   ├── family.py
│   │   │   ├── product.py
│   │   │   └── production_order.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── auth_repository.py
│   │   │   ├── idempotency_repository.py
│   │   │   ├── machine_repository.py
│   │   │   ├── family_repository.py
│   │   │   ├── product_repository.py
│   │   │   └── production_order_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── idempotency_service.py
│   │   │   ├── machine_service.py
│   │   │   ├── family_service.py
│   │   │   ├── product_service.py
│   │   │   └── production_order_service.py
│   │   │
│   │   └── scheduling/                  # Previsto para próximas releases
│   │       ├── __init__.py
│   │       ├── types.py
│   │       ├── constraints.py
│   │       ├── heuristics.py
│   │       ├── scoring.py
│   │       └── engine.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_machine_service.py
│   │   │   ├── test_family_service.py
│   │   │   ├── test_product_service.py
│   │   │   └── test_production_order_service.py
│   │   ├── integration/
│   │   │   ├── test_auth_api.py
│   │   │   ├── test_users_api.py
│   │   │   ├── test_machines_api.py
│   │   │   ├── test_families_api.py
│   │   │   ├── test_products_api.py
│   │   │   ├── test_production_orders_api.py
│   │   │   └── drivers/
│   │   │       ├── test_data_integrity.py
│   │   │       ├── test_idempotency.py
│   │   │       ├── test_concurrent_updates.py
│   │   │       ├── test_access_control.py
│   │   │       ├── test_login_lockout.py
│   │   │       └── test_session_lifecycle.py
│   │   └── conftest.py
│   │
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml                   # Configuração de qualidade de código
│   ├── pytest.ini
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   └── logo/
│   │       ├── setupflow-logo.svg
│   │       ├── setupflow-wordmark.svg
│   │       └── setupflow-symbol.svg
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   └── images/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   └── forms/
│   │   ├── pages/
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Machines/
│   │   │   ├── Families/
│   │   │   ├── Products/
│   │   │   └── ProductionOrders/
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   ├── machineService.ts
│   │   │   ├── familyService.ts
│   │   │   ├── productService.ts
│   │   │   └── productionOrderService.ts
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── routes/
│   │   │   ├── AppRoutes.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── machine.ts
│   │   │   ├── family.ts
│   │   │   ├── product.ts
│   │   │   └── productionOrder.ts
│   │   ├── utils/
│   │   ├── tests/
│   │   │   ├── setup.ts
│   │   │   ├── components/
│   │   │   └── pages/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── eslint.config.js
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── README.md
│
├── cypress/
│   ├── e2e/
│   │   ├── login.feature
│   │   ├── controle-acesso.feature
│   │   ├── cadastro-maquina.feature
│   │   ├── cadastro-familia.feature
│   │   ├── cadastro-produto.feature
│   │   └── cadastro-ordem-producao.feature
│   ├── fixtures/
│   │   └── test-data.json
│   ├── support/
│   │   ├── step_definitions/
│   │   │   ├── login.steps.ts
│   │   │   ├── access-control.steps.ts
│   │   │   ├── machines.steps.ts
│   │   │   ├── families.steps.ts
│   │   │   ├── products.steps.ts
│   │   │   └── production-orders.steps.ts
│   │   ├── commands.ts
│   │   └── e2e.ts
│   └── tsconfig.json
│
├── tests/
│   └── performance/                    # Testes k6 das próximas releases
│       ├── driver07.js
│       ├── driver08.js
│       ├── driver09.js
│       └── README.md
│
├── docs/
│   ├── arquitetura/
│   │   ├── arquitetura-setupflow.png
│   │   ├── arquitetura.md
│   │   └── modelo-de-dados.md
│   ├── planejamento/
│   │   ├── backlog.md
│   │   ├── plano-de-releases.md
│   │   └── dependencias-us.md
│   ├── qualidade/
│   │   ├── plano-de-qualidade.xlsx
│   │   ├── plano-de-teste.md
│   │   ├── drivers-arquiteturais.md
│   │   └── definition-of-done.xlsx
│   ├── riscos/
│   │   └── plano-de-riscos.xlsx
│   ├── sprints/
│   │   ├── sprint-00/
│   │   │   └── README.md
│   │   ├── sprint-01/
│   │   │   ├── planning.md
│   │   │   ├── review.md
│   │   │   └── retrospectiva.md
│   │   └── README.md
│   ├── releases/
│   │   └── release-01.md
│   └── setup/
│       └── ambiente-desenvolvimento.md
│
├── scripts/
│   ├── setup_backend.ps1
│   └── setup_frontend.ps1
│
├── compose.yaml
├── cypress.config.ts
├── .cypress-cucumber-preprocessorrc.json
├── package.json                        # Dependências e comandos de E2E
├── package-lock.json
├── .env.example                        # Variáveis do Docker Compose
├── .gitignore
├── LICENSE
└── README.md
```

### Responsabilidades das camadas

| Diretório | Responsabilidade |
|---|---|
| `backend/app/api/` | Rotas HTTP e dependências das requisições. |
| `backend/app/core/` | Configurações, segurança e recursos compartilhados. |
| `backend/app/database/` | Conexão, sessões e base do ORM. |
| `backend/app/models/` | Modelos persistidos no PostgreSQL. |
| `backend/app/schemas/` | Validação de entradas e definição das respostas. |
| `backend/app/repositories/` | Consultas e operações de persistência. |
| `backend/app/services/` | Regras de negócio e coordenação das transações. |
| `backend/app/scheduling/` | Algoritmos de sequenciamento independentes da API e do banco. |
| `frontend/src/` | Interface, navegação e comunicação com a API. |
| `cypress/` | Testes ponta a ponta com Cypress e Gherkin. |
| `tests/performance/` | Testes dos drivers de desempenho. |
| `docs/` | Documentação técnica e acompanhamento do projeto. |

### Convenções

- A estrutura apresentada é a organização planejada; os arquivos serão adicionados conforme a implementação.
- As rotas delegam as regras de negócio aos serviços.
- Os serviços coordenam as transações; os repositórios não executam commits independentes.
- As permissões são verificadas no backend, mesmo quando a interface restringe o acesso.
- Segredos e arquivos `.env` não são versionados; os arquivos `.env.example` documentam as variáveis necessárias.
- Os arquivos de dependências e seus locks são mantidos no repositório.
- Os testes e as evidências devem ser vinculados às US e aos drivers correspondentes.
- Quando o Jira for a fonte oficial do backlog, a documentação deve referenciá-lo para evitar versões divergentes.
