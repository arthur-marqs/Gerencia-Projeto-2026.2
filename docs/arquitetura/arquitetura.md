# Arquitetura do SetupFlow

**Versão:** 0.1 — proposta para implementação  
**Data:** 22/10/2026  
**Estado:** arquitetura planejada.

## 1. Objetivo e contexto

O SetupFlow é uma aplicação web responsiva para apoiar o sequenciamento da produção em pequenas e médias indústrias. Sugere sequências considerando tempos de setup, prazos, prioridades e restrições das máquinas, permitindo comparação, aprovação, acompanhamento e replanejamento.

A proposta do projeto define dois perfis: **Planejador** e **Operador/Supervisor**. Um aplicativo móvel nativo não faz parte do MVP. Os papéis acadêmicos PO, SM, QA e DevOps são responsabilidades da equipe e não devem ser confundidos com perfis de acesso da aplicação.

## 2. Visão geral

![Arquitetura proposta do SetupFlow](arquitetura-setupflow.png)

O backend é uma única aplicação FastAPI organizada por camadas. Frontend e backend são aplicações distintas dentro do mesmo repositório. O PostgreSQL concentra a persistência. O algoritmo de sequenciamento pertence ao backend e não é um serviço separado.

| Componente | Tecnologia planejada | Responsabilidade |
|---|---|---|
| Interface web | React, TypeScript e Vite | Formulários, navegação, planejamento e acompanhamento. |
| API | Python, FastAPI e Pydantic | Contrato HTTP, validação de entrada e autorização. |
| Persistência | SQLAlchemy, psycopg e PostgreSQL | Consultas, transações, relacionamentos e restrições. |
| Migrações | Alembic | Evolução versionada do banco. |
| Sequenciamento | Python | Heurísticas, validação das restrições e avaliação das sequências. |
| Testes | Pytest/HTTPX, Vitest e Cypress/Gherkin | Regras, API, componentes e fluxos ponta a ponta. |
| Desempenho | k6 | Cenários dos drivers 07, 08 e 09, com carga definida nas especificações. |
| Automação | GitHub Actions | Instalação, análise de código, testes e build. |
| Ambiente local | Docker Compose | Serviços e configurações reproduzíveis. |

As versões das dependências devem ser fixadas e alinhadas ao CI. A escolha final de componentes visuais permanece uma decisão da equipe: a estrutura recente contempla Tailwind, enquanto a sugestão inicial usava MUI.

## 3. Organização por camadas

| Caminho | Responsabilidade | Limite |
|---|---|---|
| `backend/app/main.py` | Criar a aplicação e registrar rotas e middleware. | Não concentrar regras de negócio. |
| `backend/app/api/routes/` | Receber requisições e chamar serviços. | Não realizar gravações diretamente. |
| `backend/app/api/deps.py` | Disponibilizar sessão do banco e usuário autenticado. | Não duplicar regras de negócio. |
| `backend/app/schemas/` | Definir entradas e respostas. | Não substituir validações que dependem do estado do banco. |
| `backend/app/services/` | Aplicar regras e controlar a transação completa. | Não depender de detalhes da interface React. |
| `backend/app/repositories/` | Consultar, inserir e atualizar dados. | Não executar commits independentes por método. |
| `backend/app/models/` | Mapear entidades e restrições persistidas. | Não usar os modelos diretamente como contrato público da API. |
| `backend/app/database/` | Configurar engine, sessões e base do ORM. | Obter credenciais de configuração externa. |
| `backend/app/core/` | Configuração, segurança, permissões e erros comuns. | Evitar transformá-lo em depósito de regras específicas. |
| `backend/app/scheduling/` | Executar o algoritmo com estruturas de entrada e saída. | Não acessar banco, cookies ou requisições HTTP. |

Os módulos futuros de planejamento, setups, execução e indicadores terão arquivos nas mesmas camadas. Não é necessário criar arquivos vazios para todo o escopo na primeira sprint.

## 4. Fluxo de cadastro de uma ordem

1. A interface envia os dados e uma chave de idempotência para `POST /api/v1/production-orders` — caminho proposto.
2. A API valida o formato, identifica a sessão e verifica a permissão.
3. O serviço valida produto, quantidade, prazo e demais regras do caso de uso.
4. Na mesma transação, registra a chave de idempotência e a ordem por meio dos repositórios.
5. O serviço confirma a transação; somente depois a API responde sucesso.
6. Um reenvio com a mesma chave e conteúdo recupera o resultado anterior. A mesma chave com conteúdo diferente é rejeitada como conflito.

A chave é vinculada ao usuário e ao tipo de operação, com restrição única no banco. A interface reutiliza a chave em tentativas da mesma operação e cria outra para um novo cadastro intencional. Duas requisições simultâneas precisam respeitar a mesma garantia; uma consulta prévia isolada não basta.

## 5. Autenticação e autorização

- Proposta: sessões persistidas no PostgreSQL e identificadas por token aleatório em cookie `HttpOnly`.
- Armazenar apenas o hash do token de sessão; nunca o token em texto puro no banco ou em logs.
- Em HTTPS, usar cookie `Secure`; definir `SameSite` conforme a topologia e proteção CSRF para operações que alteram dados.
- Validar expiração, revogação e situação do usuário no servidor. Logout deve revogar a sessão.
- Armazenar senhas com hash apropriado, como Argon2, sem senhas reversíveis.
- Atualizar atomicamente contadores e bloqueios de login no banco, evitando proteção somente em memória de um processo.
- Verificar autorização em cada operação protegida; `ProtectedRoute.tsx` controla a experiência da interface, não a segurança da API.

| Perfil | Responsabilidade funcional prevista |
|---|---|
| Planejador | Cadastros de produção, prioridades, geração/comparação e aprovação do planejamento. |
| Operador/Supervisor | Consulta e execução das ordens, registro de andamento, interrupções e tempos reais. |

A matriz detalhada de permissões, a criação inicial de usuários e quem pode administrar contas precisam ser validadas antes da implementação de `users.py`. Não se presume um terceiro perfil administrador.

## 6. Sequenciamento e execução

O serviço de planejamento carrega um retrato consistente dos dados, monta a entrada do algoritmo e recebe uma proposta de sequência. O algoritmo aplica critérios determinísticos, com desempates explícitos. Uma heurística não garante uma solução ótima.

Cada alternativa deve preservar entradas relevantes, resultado e métricas calculadas. Ao aprovar uma alternativa, o serviço revalida a disponibilidade das ordens, as versões e os conflitos do planejamento. Uma geração longa não deve manter transações de escrita abertas desnecessariamente.

A consulta da sequência aprovada lê o resultado persistido; não recalcula o algoritmo. O replanejamento cria uma nova revisão, preserva o histórico e mantém a ligação entre uma execução e sua ordem de produção. O tratamento de ordens já iniciadas deve ser acordado antes dessa funcionalidade.

## 7. Drivers arquiteturais



## 8. Ambiente e integração contínua

No desenvolvimento, o Compose disponibiliza os serviços configurados pela equipe. O navegador acessa a API por HTTP local. Na homologação, planejar HTTPS e, preferencialmente, um mesmo domínio com encaminhamento de `/api` ao backend; hospedagem e proxy ainda precisam ser definidos.

O GitHub Actions executa os checks em um ambiente temporário, com banco exclusivo de teste. Ele não participa do fluxo das requisições da aplicação.

Evolução do CI:

1. Instalação de dependências, Ruff/ESLint e build do frontend.
2. Pytest, migrações e testes de integração com PostgreSQL.
3. Testes de componentes e Cypress com aplicação e API iniciadas.
4. Testes de desempenho em ambiente controlado, evitando interpretar variações de runners compartilhados como medidas definitivas dos drivers.

Guardar evidências por execução e commit. Exigir os checks aplicáveis nos PRs para `main`. Deploy automatizado é uma etapa posterior e não está implementado por este documento.


## 9. Fontes e pontos de validação

- Proposta de projeto SetupFlow, versão 1.0, de 09/10/2026, consultada nesta elaboração: perfis, escopo macro e stack.
- Estrutura por camadas e decisões discutidas pela equipe nesta conversa.
- [Modelo de dados proposto](modelo-de-dados.md).
