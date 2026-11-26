# Relatório de revisão e validação — US17: Aprovar planejamento de produção

**Situação da entrega em 26/11/2026 · Aprovada pelo PO e integrada à `main`.** [PR #28](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/28) (`5772ec0`). Os sete critérios do DoD estão concluídos para o incremento aceito. [Definition of Done](../../status-projeto.md#definition-of-done-dod)

O parecer abaixo corresponde à avaliação de `40e0afd`, anterior ao merge. A correção posterior do BUG-004 foi retestada em `docs/qualidade` e aguarda integração.

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável pelo QA | Leonardo Istamilo, conforme os papéis da Release 2 |
| Data da revisão | 25/11/2026 |
| História de usuário | US17 — Aprovar planejamento de produção. Link oficial da issue não localizado. |
| Pull Request | [PR #28](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/28), integrado após a revisão. |
| Branch | `feature/US17---Aprovar-planejamento-de-produção` |
| Commit avaliado | [`40e0afd6973b36683a2c72a80ee893a6d7b782a8`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/40e0afd6973b36683a2c72a80ee893a6d7b782a8) |
| Ambiente | Local com Windows e Chrome 158. GitHub Actions com Ubuntu, PostgreSQL 18, Chrome 157 e Electron 150. |
| Parecer de QA da revisão original | **Validação inconclusiva para aceite.** Os três casos do plano passaram. Permanecem pendentes a revisão e a integração via PR, a confirmação da exigência de homologação e o aceite do PO. |

## 1. Objetivo e escopo

Verificar os critérios de aceite da US17 e a Definition of Done, com rastreabilidade aos casos CT-123, CT-124 e CT-125 do plano de testes da Sprint 3.

**Funcionalidades avaliadas** — Seleção explícita de uma sequência manual ou sugerida, registro da aprovação, consulta persistida para execução, permissões e tentativa de aprovação sem planejamento disponível.

**Driver relacionado** — Driver04, controle de acesso às operações. A avaliação cobre os endpoints da US17 e o acesso do Operador à sequência aprovada. A meta integral do driver permanece fora deste escopo.

**Limitações** — A CI avaliada foi disparada pelo `push` do commit indicado. Carregamento e falha de rede da interface foram revisados em código. A homologação e o aceite formal do PO ficaram sem evidência.

## 2. Revisão da implementação

| Aspecto | Situação | Observações / evidências |
|---|---|---|
| Comportamento previsto na US | Conforme | O Planejador aprova a sequência escolhida. O Operador consulta o planejamento aprovado e sua ordem de execução. [Cenários de aceite](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/frontend/cypress/e2e/aprovacao.feature) |
| Regras de negócio | Conforme | A aprovação preserva ordem, posição e máquina atribuída. Os testes conferem a integridade das origens, o reenvio da mesma aprovação e o bloqueio de aprovações concorrentes para as mesmas ordens. [Testes de integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/backend/testes/integration/test_us17_aprovacao.py) |
| Permissões de acesso | Conforme | A API retornou HTTP 401 sem sessão e HTTP 403 para o Operador ao tentar aprovar ou listar candidatos. O Operador autenticado consultou os aprovados. [Backend na CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331463) |
| Validações e tratamento de erros | Conforme | A API retornou HTTP 404 quando faltava planejamento e HTTP 409 quando a sequência selecionada estava desatualizada ou as ordens já tinham sido aprovadas. [Testes de integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/backend/testes/integration/test_us17_aprovacao.py) |
| Estados da interface — carregamento, vazio e erro | Não verificado integralmente | O CT-124 validou o estado vazio e a mensagem da tentativa sem planejamento. Carregamento e falha de rede foram verificados por leitura do código. [Página de aprovação](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/frontend/src/features/planejamentos/pages/AprovacoesPlanejamentoPage.tsx) |
| Testes automatizados relacionados | Conforme | A CI executou a suíte de backend e os três casos da US17 nos dois navegadores. [CI do commit](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863) |
| Documentação exigida | Conforme | A documentação descreve a migração, os endpoints, os perfis e os casos de aceite. [Backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/backend/README.md#us17--aprovar-planejamento-de-produção) · [Cypress](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/frontend/cypress/README.md#cenários-da-us17) |

## 3. Validação dos critérios de aceite

| Critério / cenário | Caso de teste | Execução | Resultado | Evidência / bug |
|---|---|---|---|---|
| C1 — Aprovar o planejamento e disponibilizá-lo para execução | CT-123 | Cypress com API e PostgreSQL reais | **Aprovado** | Status e sequência persistiram após recarregar. O Operador consultou o mesmo planejamento. [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) |
| C2 — Informar que não existe planejamento disponível para aprovação | CT-124 | Cypress e Pytest/API | **Aprovado** | A interface informou a ausência e nenhuma aprovação foi registrada. A API também foi testada diretamente. [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) · [Backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331463) |
| Integração da US17 — Aprovar a alternativa selecionada e preservar os registros de origem | CT-125 | Cypress e Pytest/API | **Aprovado** | A aprovação registrou a sugestão escolhida, com seus itens na ordem prevista. O plano manual e a sugestão permaneceram iguais. [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) · [Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331420) |

### 3.1. Registro de execução — CT-123

| Campo | Registro |
|---|---|
| Data / responsável | 25/11/2026 · execução automatizada no GitHub Actions, conferida nesta revisão |
| Commit testado | `40e0afd6973b36683a2c72a80ee893a6d7b782a8` |
| Pré-condições | Sessão de Planejador e plano manual salvo. Conta Operador disponível para a consulta posterior. |
| Dados utilizados | Sequência manual `OP01 → OP03`. |
| Resultado esperado | Registrar a origem manual e disponibilizar a sequência aprovada para consulta, preservando a ordem após recarregar. |
| Resultado obtido | A API retornou HTTP 201 com status `APROVADO`. Após recarregar, a tela manteve `OP01 → OP03`. O Operador consultou o mesmo registro e a interface omitiu a ação de aprovação para esse perfil. |
| Resultado do teste | **Aprovado** |
| Evidência | [Execução no Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) |
| Bug relacionado | Nenhum observado. |

**Passos executados**

1. Abrir **Execução da produção**, selecionar o plano manual e conferir a sequência.
2. Aprovar e verificar a origem, o status e os itens retornados.
3. Recarregar e conferir o registro. Autenticar como Operador e consultar a mesma sequência.

### 3.2. Registro de execução — CT-124

| Campo | Registro |
|---|---|
| Data / responsável | 25/11/2026 · execução automatizada no GitHub Actions, conferida nesta revisão |
| Commit testado | `40e0afd6973b36683a2c72a80ee893a6d7b782a8` |
| Pré-condições | Planejador autenticado e banco de teste sem planejamento disponível. |
| Dados utilizados | Lista de candidatos vazia. Na API, também foi usado um identificador inexistente. |
| Resultado esperado | Informar a ausência de planejamento e preservar a lista de aprovações vazia. |
| Resultado obtido | A tela exibiu “Não existe planejamento disponível para aprovação.” O Cypress confirmou que a interface não enviou o POST e que a consulta de aprovados retornou `[]`. O teste direto da API recebeu HTTP 404 para a tentativa sem planejamento. |
| Resultado do teste | **Aprovado** |
| Evidência | [Cypress no Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) · [Pytest na CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331463) |
| Bug relacionado | Nenhum observado. |

**Passos executados**

1. Abrir **Execução da produção** sem candidatos.
2. Clicar em **Aprovar planejamento** e verificar a mensagem.
3. Consultar os aprovados e confirmar que a lista continua vazia.

### 3.3. Registro de execução — CT-125

| Campo | Registro |
|---|---|
| Data / responsável | 25/11/2026 · execução automatizada no GitHub Actions, conferida nesta revisão |
| Commit testado | `40e0afd6973b36683a2c72a80ee893a6d7b782a8` |
| Pré-condições | Planejador autenticado, plano manual e sugestão disponíveis para as mesmas ordens. |
| Dados utilizados | Manual `OP01 → OP02 → OP03`, sugestão `OP01 → OP03 → OP02` e tempos de setup A→B de 20 min e B→A de 30 min. |
| Resultado esperado | Registrar exclusivamente a alternativa escolhida, com a origem e a sequência corretas, e preservar os registros do plano manual e da sugestão. |
| Resultado obtido | A tela apresentou as duas alternativas sem seleção inicial. Após escolher a sugerida, a API retornou HTTP 201 com seu identificador, posições e máquinas atribuídas. As consultas posteriores das duas origens corresponderam aos registros anteriores. |
| Resultado do teste | **Aprovado** |
| Evidência | [Cenário CT-125](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/40e0afd6973b36683a2c72a80ee893a6d7b782a8/frontend/cypress/e2e/aprovacao.feature#L30-L43) · [Execução no Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331420) |
| Bug relacionado | Nenhum observado. |

**Passos executados**

1. Criar o plano manual e gerar uma sugestão para as mesmas ordens.
2. Conferir as duas prévias e selecionar explicitamente a sugerida.
3. Aprovar e validar origem e sequência. Consultar novamente o plano manual e a sugestão para conferir a preservação dos dados.

## 4. Bugs e pendências

| Issue / referência | Descrição | Classificação | Severidade | Status | Impacto no aceite |
|---|---|---|---|---|---|
| Branch da US17 | Revisão e integração via PR aguardam registro. | Pendência da DoD | — | Pendente | Impede concluir a DoD. |
| Release 2 / Sprint 3 | Exigência de homologação e versão implantada ficaram sem comprovação. | Pendência da DoD | — | Não verificado | Depende da confirmação de aplicabilidade. |
| Aceite da US17 | Aceite formal do PO sem registro nas fontes consultadas. | Pendência da DoD | — | Não verificado | Impede concluir a DoD. |

**Situação do levantamento** — Nenhum bug identificado no escopo executado. As pendências registradas referem-se à DoD.

## 5. DoD na avaliação de `40e0afd`

**Referência** — DoD fornecida na definição da US17, Release 2 / Sprint 3.

| Critério da DoD | Situação | Evidência / pendência |
|---|---|---|
| Código revisado e integrado via Pull Request | Não atendido | A consulta ao GitHub não localizou PR para o head avaliado. `main` ainda estava em `65a1d24`. |
| Critérios de aceite atendidos e validados pelo QA | Atendido no escopo desta avaliação | C1 e C2 passaram, assim como o cenário de integração CT-125. |
| Testes escritos e passando | Atendido | Sete testes de integração da US17 passaram dentro da suíte de backend. Os três casos do plano passaram no Chrome e no Electron. |
| Pipeline de CI sem falhas | Atendido | Todos os jobs da CI do commit `40e0afd` concluíram com sucesso. [CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863) |
| Implantado em ambiente de homologação, quando exigido na release | Não verificado | A exigência de homologação e a versão implantada precisam de confirmação. |
| Documentação atualizada | Atendido | Guias do backend e do Cypress descrevem a US17, a migração e a cobertura de aceite. |
| Aceita pelo PO | Não verificado | Aceite formal sem registro nas fontes consultadas. |

## 6. Reteste e regressão

**Escopo da regressão** — Planejamento manual, geração e consulta de sugestões, comparação de alternativas e compatibilidade de máquinas. A aprovação consome essas sequências e acrescenta uma regra de disponibilidade para as ordens. A suíte de backend também cobre persistência e permissões.

| Data | Tipo | Caso / fluxo | Bug relacionado | Commit | Resultado | Evidência |
|---|---|---|---|---|---|---|
| 25/11/2026 | Regressão local | US17, comparação da US16, consulta de sugestão e compatibilidade | — | `65a1d24` com a implementação local da US17 | **9/9 aprovados** | Registro local `.tmp/qa-us17/e2e-chrome-regressao/run-summary.json` |
| 25/11/2026 | Regressão na CI | Suíte completa do backend | — | `40e0afd` | **280/280 aprovados** | [Backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331463) |
| 25/11/2026 | Regressão na CI | Cenários de aceite com serviços reais | — | `40e0afd` | **67/67 aprovados por navegador** | [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331430) · [Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863/job/139611331420) |
| 25/11/2026 | Verificação de migração | Aplicação da revisão `8d17b4f2c306` em banco isolado com dados existentes | — | Implementação local da US17 | **Aprovado.** Foram preservados um plano manual, uma sugestão e os itens de ambos. | Registro local `.tmp/qa-us17/migracao.json` |

**Reteste de bug** — Não se aplica a esta avaliação. A entrega consiste na implementação inicial da US17.

## 7. Resumo dos resultados

| Indicador | Quantidade |
|---|---:|
| Casos previstos nesta avaliação | 3 |
| Casos aprovados | 3 |
| Casos reprovados | 0 |
| Casos bloqueados | 0 |
| Casos não executados | 0 |
| Bugs identificados nesta avaliação | 0 |
| Bugs corrigidos com reteste aprovado | 0 |
| Bugs ainda pendentes no escopo avaliado | 0 |

Os indicadores contam CT-123, CT-124 e CT-125 uma vez cada. Os totais de regressão são registrados por execução na seção 6.

## 8. Parecer de QA anterior à integração

**Parecer — Validação inconclusiva para aceite.**

**Commit ao qual o parecer se aplica** — `40e0afd6973b36683a2c72a80ee893a6d7b782a8`.

**Justificativa** — Os critérios de aceite e a preservação da alternativa escolhida foram verificados em ambiente integrado. A CI do commit passou com 280 testes de backend e 67 cenários em cada navegador. A conclusão do aceite ainda depende das condições de entrega da DoD. [CI da US17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45730592863)

### Pendências para conclusão

| Pendência | Responsável | Referência | Situação |
|---|---|---|---|
| Vincular a issue e registrar revisão e integração via PR | Leonardo Istamilo e revisores do PR | US17 / branch da história | Pendente |
| Confirmar se a release exige homologação e registrar a versão implantada, quando aplicável | PO e equipe da release | DoD da US17 | Não verificado |
| Registrar o aceite formal da história | Arthur Marques, PO | US17 | Pendente |

**Riscos ou limitações remanescentes** — A CI disponível é do push da branch. Os estados de carregamento e falha de rede da página foram conferidos por revisão estática. A execução em homologação depende da confirmação indicada acima.

**Aceite do PO, quando aplicável** — Pendente de registro.

## 9. Histórico da revisão

| Data | Responsável | Commit avaliado | Atualização |
|---|---|---|---|
| 25/11/2026 | Validação local da implementação | `65a1d24` com as alterações da US17 | 280 testes de backend e 9 cenários no Chrome passaram. A migração preservou as sequências da massa de teste. |
| 25/11/2026 | CI e revisão de QA | `40e0afd6973b36683a2c72a80ee893a6d7b782a8` | CT-123, CT-124 e CT-125 passaram no Chrome e no Electron. A CI concluiu com sucesso. O aceite permanece inconclusivo pelas pendências da DoD. |

## Acompanhamento do BUG-004

Em 26/11/2026, o reteste local do [BUG-004 / issue #30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) confirmou a recusa de aprovação quando a máquina fica inativa ou perde a compatibilidade após a geração. CT-123, CT-124 e CT-125 passaram novamente no Chrome. O resultado se aplica ao código da correção, com integração à `main` pendente. [Relatório de reteste](auditoria-bugs/reteste-bug004.md)
