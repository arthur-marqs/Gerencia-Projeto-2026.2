# Arquitetura do SetupFlow

Atualizado em 26/11/2026. O SetupFlow é uma aplicação web para cadastros e planejamento da produção. O incremento integrado cobre planejamento manual, geração e comparação de sequências, aprovação pelo Planejador e consulta pelo Operador. [Entregas integradas](../status-projeto.md)

## Visão geral

O frontend usa React, TypeScript, Vite e Tailwind CSS. A API FastAPI valida os dados com Pydantic e acessa o PostgreSQL com SQLAlchemy e psycopg. O Alembic aplica o esquema versionado. O sequenciamento executa no mesmo backend que atende à API. [Mapa do repositório](../estrutura-projeto.md) · [Desenho da proposta original](Arquitetura-SetupFlow.png)

| Caminho | Responsabilidade |
| --- | --- |
| `frontend/src/features/` | Telas de autenticação, usuários, cadastros, ordens e planejamento. |
| `backend/app/main.py` | Criação da aplicação, registro dos routers e configuração de CORS. |
| `backend/app/api/routes/` | Operações HTTP, consultas, gravações e coordenação das transações. |
| `backend/app/api/deps.py` | Sessão SQLAlchemy, identificação do usuário e autorização por perfil. |
| `backend/app/schemas/` · `backend/app/models/` | Contratos de entrada e saída e mapeamento das tabelas. |
| `backend/app/services/` | Cálculo das sequências e distribuição das ordens nas máquinas. |
| `backend/app/db/` · `backend/app/core/` | Conexão com PostgreSQL, configuração e funções de segurança. |

## Autenticação e autorização

O login verifica a senha armazenada em hash, registra a sessão em PostgreSQL e entrega um cookie `HttpOnly`. A API verifica validade, expiração, revogação e situação da conta nas chamadas protegidas. O logout invalida a sessão. O controle de tentativas usa identificador de login e IP, com persistência no banco.

| Perfil | Acesso implementado |
| --- | --- |
| `PLANEJADOR` | Cadastros de produção, tempos de setup, ordens, planejamento manual, sugestões, comparação e aprovação. |
| `OPERADOR` | Consulta da sequência registrada em Execução da produção. |
| `ADMINISTRADOR` | Gerenciamento de contas e perfis. |

Uma conta pode ter mais de um perfil. A navegação exibe os módulos permitidos e a API confirma o acesso em cada operação protegida. [Gestão de usuários](../../backend/README.md#us-32--gerenciamento-de-usuários)

## Cadastro e atualização de ordens

O frontend envia o cadastro para `POST /api/ordens-producao` com uma `Idempotency-Key` em UUID. O banco garante a unicidade do par usuário e chave. A ordem e a operação são gravadas na mesma transação. Se a mesma chave e o mesmo conteúdo forem reenviados, a API devolve a ordem original. A mesma chave com conteúdo diferente resulta em HTTP 409.

Em falha de comunicação nas gravações de cadastro, duração estimada, prazo e prioridade, a API tenta desfazer a transação e responde HTTP 503. [Idempotência e integridade](../../backend/README.md#idempotência-no-cadastro-de-ordens-driver02)

## Sequenciamento e execução

O Planejador pode montar e editar uma sequência manual com ordens pendentes. Para sugerir uma sequência, a API usa as ordens selecionadas, seus prazos, prioridades e durações, os tempos direcionais de setup e as compatibilidades com máquinas ativas. A geração persiste a sugestão e seus itens. Ao comparar, a API lê os resultados armazenados e preserva os planos de origem.

O Planejador aprova uma alternativa, manual ou sugerida. A API grava origem, autor, data e sequência. As restrições do banco garantem uma aprovação por origem e impedem que a mesma ordem integre duas aprovações. O Operador consulta os dados persistidos em Execução da produção. O registro de início, conclusão e interrupções, o replanejamento e os indicadores fazem parte da evolução. [Regras de aprovação](../../backend/README.md#us17--aprovar-planejamento-de-produção) · [Modelo de dados](modelo-de-dados.md)

## Drivers arquiteturais

Os Drivers 01, 02, 04, 05 e 06 estão integrados e foram aceitos pelo PO. A auditoria descreve os testes de consistência, idempotência, autorização, limitação de tentativas e expiração de sessão. [Rastreabilidade e evidências](../qualidade/release-2/auditoria-bugs/relatorio-validacao.md#drivers)

## Ambiente e integração contínua

O ambiente local usa o servidor Vite, a API Uvicorn e PostgreSQL. O GitHub Actions usa serviços PostgreSQL exclusivos para Pytest e Cypress. O pipeline executa verificações em pushes e PRs, incluindo lint e build, e publica relatórios JUnit e evidências do navegador. [Configuração local](../../README.md#como-executar-localmente) · [CI da versão integrada](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972)
