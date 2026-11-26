# Relatório de revisão e validação — Driver04: Controle de acesso às operações

**Situação da entrega em 26/11/2026 · Aprovado pelo PO e integrado à `main`.** [PR #29](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/29) (`08a62f5`). Os sete critérios do DoD estão concluídos para o incremento aceito. [Definition of Done](../../status-projeto.md#definition-of-done-dod)

A auditoria integrada também exercitou as rotas de aprovação e ampliou a matriz para 28 recusas e 14 controles positivos. Os resultados abaixo pertencem à revisão de `20c7bc4`. [Auditoria integrada](auditoria-bugs/relatorio-validacao.md#drivers)

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável pelo QA | Leonardo Istamilo |
| Data da revisão | 26/11/2026, America/Sao_Paulo |
| Item avaliado | Driver04 — Controle de acesso às operações. Definição fornecida na solicitação. A issue oficial não foi localizada. |
| Pull Request | [PR #29](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/29), integrado após a revisão. |
| Branch | `feature/driver04-controle-acesso` |
| Commit avaliado | [`20c7bc44de3778491652552743dcb01558b44f03`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/20c7bc44de3778491652552743dcb01558b44f03) |
| Ambiente | Matriz local com Windows, Python 3.11, FastAPI TestClient e PostgreSQL 18.6 em instância descartável. A CI do commit usou Ubuntu, PostgreSQL 18, Chrome 157 e Electron 150. |
| Parecer de QA da revisão original | **Validação inconclusiva para aceite.** A meta técnica foi comprovada na matriz avaliada. A conclusão depende das pendências de integração, cobertura e DoD registradas neste relatório. |

## 1. Objetivo e escopo

Verificar se a API autentica e autoriza o usuário antes de atender operações restritas ao Planejador. A medida exige **100% de rejeição em pelo menos 20 tentativas distintas não autorizadas**, sem exposição de dados protegidos e sem alterações indevidas no banco. O plano de testes da Sprint 3, revisão 2.4, exige ao menos dez combinações para cada condição, dados de negócio válidos e controle positivo separado.

**Funcionalidades avaliadas** — Consultas e operações de máquinas, tempos de setup, geração e consulta de sugestões, comparação de sequências e consulta e edição de planejamento manual. O estímulo foi aplicado por chamadas à API com usuário de teste autenticado como `OPERADOR` ou com a sessão ausente.

**Drivers relacionados** — Driver06, pela dependência comum de sessão. Expiração, invalidação e tempo de resposta do Driver06 pertencem a avaliação própria.

**Limitações** — O commit avaliado deriva de `65a1d24`. A aprovação de planejamento já constava em `main` no commit `5772ec0` via PR #28, porém a rota não existe no head do Driver04. A edição manual foi exercitada. O fluxo de replanejamento com nova revisão ficou pendente conforme o plano. A matriz usa o perfil `OPERADOR`, que existe no produto. A necessidade de um perfil `SUPERVISOR` separado aguarda confirmação. [Integração da US17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/28)

A DoR foi informada como concluída na solicitação. Os estados da DoD são avaliados na seção 5.

## 2. Revisão da implementação

| Aspecto | Situação | Observações / evidências |
|---|---|---|
| Comportamento previsto no driver | Conforme | A matriz obteve HTTP 403 com Operador e HTTP 401 sem sessão. Foram 24 respostas com somente o `detail` esperado e 24 comparações das linhas das tabelas sem diferença. [JUnit da matriz](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) |
| Regras de negócio | Conforme | Cada operação da matriz também foi solicitada por Planejador, em massa de teste equivalente. As cinco leituras retornaram dados e as sete escritas produziram diferenças na comparação do banco. [Matriz de QA](evidencias-driver04/reavaliacao-20c7bc4/matriz-qa.py) |
| Permissões de acesso | Conforme | `get_current_user` valida sessão e usuário ativo. `require_profiles` verifica os perfis associados antes da operação protegida. A verificação foi exercitada na API. [Dependências da API](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/20c7bc44de3778491652552743dcb01558b44f03/backend/app/api/deps.py) |
| Validações e tratamento de erros | Conforme | Os corpos das respostas 401 e 403 corresponderam exatamente às mensagens esperadas. Dados e identificadores válidos foram corroborados por controles positivos na mesma matriz. [JUnit da matriz](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) |
| Estados da interface — carregamento, vazio e erro | Não se aplica à medida | A medida do Driver04 verifica requisições diretas ao servidor. O navegador foi usado nos controles positivos de planejamento. |
| Testes automatizados relacionados | Conforme na revisão | A suíte oficial passou em 44 casos na CI. A matriz complementar supera a lacuna dos corpos vazios e IDs inexistentes nessa suíte. A execução complementar ocorreu localmente. [Suíte oficial](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/20c7bc44de3778491652552743dcb01558b44f03/backend/testes/integration/drivers/test_driver04_controle_acesso.py) |
| Documentação exigida | Conforme no escopo consultado | A matriz, os comandos, as evidências e a cobertura pendente estão registrados neste relatório. A versão anterior está preservada no commit avaliado. [Relatório anterior](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/20c7bc44de3778491652552743dcb01558b44f03/docs/qualidade/release-2/revisao-driver04.md) |

## 3. Validação dos critérios de aceite

| Critério / cenário | Caso de teste | Execução | Resultado | Evidência / bug |
|---|---|---|---|---|
| C1 — Negar operações do Planejador ao Operador | CT-130 | Pytest/API com PostgreSQL real | **Aprovado — 12/12** | HTTP 403, somente `detail` e dados persistidos idênticos antes e depois em todos os casos. [JUnit](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) |
| C2 — Negar acesso direto sem autenticação | CT-131 | Pytest/API com PostgreSQL real | **Aprovado — 12/12** | HTTP 401, somente `detail` e dados persistidos idênticos antes e depois em todos os casos. [JUnit](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) |
| Controle positivo — Planejador com dados válidos | CT-132 | Pytest/API local e Cypress na CI do mesmo SHA | **Aprovado** | 12/12 controles da matriz. CT-110, CT-120 e o cenário de máquinas compatíveis também passaram no Chrome da CI. [JUnit](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) · [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620/job/139661419106) |

### 3.1. Matriz e dados válidos

Cada linha foi executada nas três condições de acesso. Foram utilizadas contas fictícias e fixtures isoladas, com máquinas M01 e M02, famílias A/B/C, ordens OP01/OP02/OP03, plano manual e sugestão persistidos. As máquinas referenciadas e os identificadores do plano e da sugestão existiam na massa. A exclusão autorizada usou M02, cadastrada para teste e sem vínculos.

| Operação | Dados ou condição do controle | CT-130 | CT-131 | CT-132 |
|---|---|---:|---:|---:|
| GET máquinas | Catálogo preenchido | 403 | 401 | 200 |
| POST máquina | Código MQA e nome válidos | 403 | 401 | 201 |
| PUT máquina | M01 existente e novo nome | 403 | 401 | 200 |
| PATCH status de máquina | M01 ativa, alteração para inativa | 403 | 401 | 200 |
| DELETE máquina | M02 existente, sem vínculos | 403 | 401 | 204 |
| GET tempos de setup | Matriz com trocas A→B e B→A | 403 | 401 | 200 |
| POST tempo de setup | A→C com 15 min e sem cadastro anterior | 403 | 401 | 201 |
| POST sugestão | OP01, OP02 e OP03 elegíveis | 403 | 401 | 201 |
| GET sugestão por ID | Sugestão existente | 403 | 401 | 200 |
| GET comparação | Plano e sugestão das mesmas ordens | 403 | 401 | 200 |
| GET planejamento por ID | Plano manual existente | 403 | 401 | 200 |
| PUT planejamento | Inversão da ordem das operações do plano manual | 403 | 401 | 200 |

### 3.2. Registro de execução — CT-130

| Campo | Registro |
|---|---|
| Data / responsável | 26/11/2026 · matriz local de QA |
| Commit testado | `20c7bc44de3778491652552743dcb01558b44f03`, extraído em cópia isolada |
| Pré-condições e dados | Massa da seção 3.1 e conta ativa autenticada com perfil `OPERADOR`. |
| Resultado esperado | 403 em cada operação, resposta de acesso negado e preservação dos dados. |
| Resultado obtido | 12/12 respostas 403. Em todas, o corpo foi somente `{"detail": "Acesso não autorizado para este perfil."}` e a comparação do banco foi idêntica. |
| Resultado do teste | **Aprovado** |
| Evidência / bug | [JUnit da matriz](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml). Nenhum bug observado. |

1. Preparar os dados e autenticar o Operador de teste.
2. Registrar a impressão digital das linhas das tabelas após o login e enviar a operação.
3. Conferir resposta e repetir a leitura das tabelas após a requisição.

### 3.3. Registro de execução — CT-131

| Campo | Registro |
|---|---|
| Data / responsável | 26/11/2026 · matriz local de QA |
| Commit testado | `20c7bc44de3778491652552743dcb01558b44f03`, extraído em cópia isolada |
| Pré-condições e dados | Massa da seção 3.1 e cliente de teste sem cookie de sessão. |
| Resultado esperado | 401 em cada operação, resposta de sessão inválida e preservação dos dados. |
| Resultado obtido | 12/12 respostas 401. Em todas, o corpo foi somente `{"detail": "Sessão inválida ou expirada."}` e a comparação do banco foi idêntica. |
| Resultado do teste | **Aprovado** |
| Evidência / bug | [JUnit da matriz](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml). Nenhum bug observado. |

1. Preparar os dados e limpar os cookies do cliente de teste.
2. Registrar a impressão digital das linhas das tabelas e enviar a operação.
3. Conferir resposta e repetir a leitura das tabelas após a requisição.

### 3.4. Registro de execução — CT-132

| Campo | Registro |
|---|---|
| Data / responsável | 26/11/2026 · matriz local de QA e auditoria dos logs da CI |
| Commit testado | `20c7bc44de3778491652552743dcb01558b44f03` |
| Pré-condições e dados | Massa da seção 3.1 e sessão ativa de Planejador. |
| Resultado esperado | Permitir as operações válidas de leitura e escrita. |
| Resultado obtido | 12/12 controles API passaram com HTTP 200, 201 ou 204 conforme a operação. As cinco leituras preservaram as linhas, as sete escritas alteraram o estado de teste e os controles de geração, consulta, comparação e compatibilidade passaram no navegador. |
| Resultado do teste | **Aprovado** |
| Evidência / bug | [JUnit da matriz](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) · [Chrome na CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620/job/139661419106). Nenhum bug observado. |

1. Repetir as operações com o perfil Planejador autenticado.
2. Verificar as respostas válidas e o efeito correspondente no banco.
3. Conferir na CI a execução dos cenários existentes CT-110, CT-120 e US15_CT01 como evidência de navegador.

**Medição** — **24/24 tentativas não autorizadas rejeitadas, 100%**, com zero exposição de dados protegidos e zero diferenças nas linhas das tabelas inspecionadas. Foram 12 operações em cada condição, superando o mínimo de 10 por condição e de 20 no total. Os 12 controles positivos e as 44 verificações da suíte oficial são registrados separadamente.

## 4. Bugs e pendências

| Issue / referência | Descrição | Classificação | Severidade | Status | Impacto no aceite |
|---|---|---|---|---|---|
| CT-130 a CT-132 | A suíte oficial usa corpos vazios e IDs inexistentes em parte dos casos. A reavaliação cobriu dados válidos com uma matriz complementar local. | Pendência de cobertura | — | Parcialmente resolvida | A medida local foi comprovada. Falta incorporar à CI a cobertura com dados válidos. |
| Integração do Driver04 | A branch está publicada, com CI de push verde. O head ainda está fora da ancestralidade da `main` consultada e o PR do Driver04 ainda não foi localizado. | Pendência da DoD | — | Pendente | Falta rever e testar a versão a integrar. |
| Aprovação e replanejamento | A aprovação da US17 já existe em `main` e precisa ser verificada na versão de integração. O replanejamento completo permanece indisponível no head avaliado. | Pendência de cobertura | — | Pendente | Esses fluxos permanecem fora da medição efetuada. |
| Perfil Supervisor | Confirmar se a denominação Operador/Supervisor indica o perfil atual `OPERADOR` ou um perfil independente. | Pendência de requisito | — | A confirmar | A evidência de C1 se aplica ao Operador disponível. |

**Situação do levantamento** — Nenhum bug funcional observado nos casos executados. Os achados registrados dizem respeito à cobertura, aos requisitos e às condições de entrega.

## 5. DoD na avaliação de `20c7bc4`

**Referência** — Critérios de saída do plano de testes da Release 2 / Sprint 3 e checklist da revisão anterior. A DoD formal específica do Driver04 ficou sem comprovação nas fontes consultadas.

| Critério observado | Situação | Evidência / pendência |
|---|---|---|
| Critérios técnicos e meta validados | Atendido no escopo executado | CT-130 e CT-131 com 24 negativas válidas, e CT-132 com controle positivo. |
| Código revisado e integrado via Pull Request | Não atendido | PR do Driver04 ainda não localizado. A branch de referência já possui alterações adicionais de planejamento, incluindo a US17. |
| Testes escritos e passando | Atendido | 44 verificações oficiais na CI e 36 execuções na matriz complementar local. A cobertura oficial com os dados válidos segue como pendência. |
| Pipeline de CI sem falhas | Atendido | Todos os jobs do push no SHA avaliado concluíram com sucesso. [CI do commit](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620) |
| Homologação quando exigida | Não verificado | Falta confirmar a exigência da release e identificar ambiente e versão implantada. |
| Documentação atualizada | Atendido no escopo da revisão | Relatório, matriz e evidências associados ao SHA avaliado. |
| Aceite pelo PO | Não verificado | Aceite formal sem evidência consultada. |

## 6. Reteste e regressão

**Escopo** — As operações usam as dependências de sessão e perfil compartilhadas pelas rotas de cadastro, planejamento e comparação. A regressão completa verifica os fluxos existentes. A matriz local foi produzida a partir de um arquivo do Git do SHA avaliado, com banco PostgreSQL dedicado, terminado em `_test`.

| Data | Tipo | Caso / fluxo | Bug relacionado | Commit | Resultado | Evidência |
|---|---|---|---|---|---|---|
| 25/11/2026 | Histórico local | Suíte oficial + regressão completa do backend | — | `65a1d24` com a suíte local do Driver04 | 44 e 317 testes aprovados, respectivamente | [Suíte original](evidencias-driver04/pytest-driver04.txt) · [Regressão original](evidencias-driver04/pytest-regressao.txt) |
| 25–26/11/2026 | Regressão na CI | Backend, incluindo a suíte oficial do Driver04 | — | `20c7bc4` | 317/317 aprovados, incluindo os 44 do driver | [Backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620/job/139661419163) |
| 25–26/11/2026 | Regressão na CI | Aceite no navegador | — | `20c7bc4` | 64/64 aprovados por navegador | [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620/job/139661419106) · [Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45745796620/job/139661419290) |
| 26/11/2026 | Reavaliação local | Matriz com dados válidos, CT-130 a CT-132 | — | `20c7bc4` | **36/36 aprovados** em 35,71 s | [JUnit](evidencias-driver04/reavaliacao-20c7bc4/matriz-pytest.xml) |

**Reteste de bug** — Não se aplica. A reavaliação complementou a cobertura sem alterar as regras de produção.

Para reproduzir a matriz, use o código do SHA avaliado, as dependências do backend e um PostgreSQL descartável indicado por `TEST_DATABASE_URL`. Execute na pasta `backend`. Há limpeza de dados de teste entre casos.

```powershell
python -m pytest -q -p testes.integration.conftest -o junit_family=xunit1 --junitxml=matriz-pytest.xml ../docs/qualidade/release-2/evidencias-driver04/reavaliacao-20c7bc4/matriz-qa.py
```

## 7. Resumo dos resultados

| Indicador | Quantidade |
|---|---:|
| Casos previstos nesta avaliação | 3 |
| Casos aprovados | 3 |
| Casos reprovados | 0 |
| Casos bloqueados | 0 |
| Casos não executados | 0 |
| Bugs identificados nesta avaliação | 0 no escopo executado |
| Bugs corrigidos com reteste aprovado | 0 |
| Bugs ainda pendentes | 0 no escopo executado |

Os três casos são CT-130, CT-131 e CT-132. As combinações da matriz, os controles de navegador e as execuções de regressão são detalhados nas seções anteriores.

## 8. Parecer de QA anterior à integração

**Parecer — Validação inconclusiva para aceite.**

**Commit avaliado** — `20c7bc44de3778491652552743dcb01558b44f03`.

**Justificativa** — A matriz com dados válidos comprovou 24/24 rejeições, com os códigos e mensagens esperados e sem alterações indevidas nos dados inspecionados. Os controles positivos passaram e a CI do mesmo SHA concluiu com sucesso. Restam a validação da versão integrada, as pendências de cobertura e a conclusão das condições da DoD.

### Pendências para conclusão

| Pendência | Responsável | Referência | Situação |
|---|---|---|---|
| Vincular a issue e registrar revisão no PR do Driver04 | Equipe de desenvolvimento e QA | Branch do Driver04 | Pendente |
| Incorporar à CI o controle com dados válidos e verificar as permissões da aprovação na versão integrada | Equipe de desenvolvimento e QA | CT-130 a CT-132 e US17 | Pendente |
| Confirmar o significado de Supervisor e a cobertura de replanejamento | PO e equipe | Critérios do Driver04 e plano da Sprint 3 | A confirmar |
| Confirmar a DoD vigente, a aplicabilidade de homologação e o aceite | PO e equipe da release | DoD / Release 2 | Não verificado |

**Riscos ou limitações remanescentes** — A matriz mede o conteúdo das linhas no banco de teste sob as condições declaradas. A CI consultada é do push da branch. Aprovação e replanejamento ficaram fora da execução do head avaliado.

**Aceite do PO** — Pendente de registro.

## 9. Histórico da revisão

| Data | Responsável | Commit avaliado | Atualização |
|---|---|---|---|
| 25/11/2026 | Avaliação original | `65a1d24` com alterações locais do Driver04 | 44 casos da suíte específica e 317 testes de regressão aprovados localmente. [Relatório original completo](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/20c7bc44de3778491652552743dcb01558b44f03/docs/qualidade/release-2/revisao-driver04.md) |
| 26/11/2026 | Leonardo Istamilo, QA da release | `20c7bc44de3778491652552743dcb01558b44f03` | Matriz complementar com 24 negativas e 12 controles aprovados. CI auditada pelo SHA. Parecer atualizado conforme as pendências de integração e cobertura. |
