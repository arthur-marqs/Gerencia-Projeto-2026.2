# Revisão de QA da US16 — Comparar sequência manual e sequência sugerida

**Situação da entrega em 26/11/2026 · Aprovada pelo PO e integrada à `main`.** [PR #27](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/27) (`10cdd8a`). Os sete critérios do DoD estão concluídos para o incremento aceito. [Definition of Done](../../status-projeto.md#definition-of-done-dod)

A correção do catálogo foi integrada com a história. O reteste de `1e98b76` confirma que o Planejador consegue abrir a comparação durante um 503 do catálogo.

## Reteste da correção do catálogo

Em 25/11/2026, o cenário automatizado `@US16_Catalogo` foi executado no Windows com Chrome 158, Cypress 16.3.0 e Node 26.13.0. O teste usou FastAPI, frontend compilado e PostgreSQL 18.6 em instância isolada. A resposta 503 foi injetada somente em `GET /api/maquinas`. As demais chamadas usaram a API e o banco de teste.

| Execução | Resultado | Evidência |
| --- | --- | --- |
| Reprodução antes da correção, `03cffae` com o cenário novo na árvore de trabalho | O teste reprovou porque o cartão do plano ficou ausente com o 503. | [Resumo anterior](evidencias-us16/reteste-catalogo-1e98b76/antes-cypress.json) · [JUnit da reprodução](evidencias-us16/reteste-catalogo-1e98b76/antes-junit.xml) |
| Reteste da correção em `1e98b763e7fedfe195f4d9c1dd3f95665187bea9` | **Aprovado.** A ordem OP04 continuou selecionável. O cartão abriu a comparação, exibindo as duas sequências e os tempos de setup de 50 e 20 minutos. O aviso do catálogo e o identificador da máquina apareceram durante a falha. Ao reabrir com catálogo saudável, a máquina M01 voltou a ser exibida pelo nome. | [JUnit da US16](evidencias-us16/reteste-catalogo-1e98b76/depois-us16-junit.xml) · [Cenário automatizado](../../../frontend/cypress/e2e/comparacao.feature#L36-L47) · [Consultas independentes](../../../frontend/src/features/planejamentos/pages/PlanejamentosPage.tsx#L53-L98) |

Para retestar, prepare o ambiente descrito no [guia do Cypress](../../../frontend/cypress/README.md) e execute a partir de `frontend`.

```powershell
npm run test:e2e -- --browser chrome --tags '@US16_Catalogo'
npm run test:e2e -- --browser chrome --tags '(@US11 or @US13 or @US14 or @US15 or @US16) and not @wip'
npm run test:e2e -- --browser chrome --tags '@CT85'
```

A regressão integrada partiu da árvore limpa em `1e98b76`. Passaram 31 dos 32 cenários de matriz de setup, geração e consulta de sugestões, prazos, prioridades, compatibilidade e comparação. CT-120, CT-121, CT-122 e `@US16_Catalogo` passaram. O CT-85 foi interrompido na preparação da massa por falha de alocação de memória no Argon2, antes do exercício da API. [Resumo da regressão](evidencias-us16/reteste-catalogo-1e98b76/regressao-cypress.json) · [JUnit da suíte de sugestões](evidencias-us16/reteste-catalogo-1e98b76/regressao-sugestao-junit.xml)

O CT-85 passou na reexecução isolada. O resumo do Cypress registra o mesmo commit e a mesma impressão digital dos arquivos de código e teste. Na reexecução, havia alterações locais apenas no relatório e nas evidências. O resultado mais recente dos 32 cenários é aprovado. O lint e o build do frontend também passaram. [Resultado da reexecução do CT-85](evidencias-us16/reteste-catalogo-1e98b76/ct85-cypress.json)

A CI citada na avaliação anterior corresponde a `03cffae`. A evidência deste reteste foi produzida localmente. Os registros abaixo preservam as constatações anteriores à correção.

## Avaliação anterior em `03cffae`

> **Parecer na avaliação anterior — Validação inconclusiva para aceite em `03cffae`.** CT-120, CT-121 e CT-122 passaram no ambiente local e na CI. A indisponibilidade simulada do catálogo de máquinas voltou a esconder os cartões e também impediu acessar a comparação pela interface. Faltavam o tratamento desse defeito e a comprovação das condições de entrega.

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Item | US16 — Comparar sequência manual e sequência sugerida. Release 2, Sprint 3. |
| Referência | História e critérios C1 e C2 fornecidos na conversa. CT-120 a CT-122 no anexo `Plano-de-Teste-SetupFlow-3.md`, revisão 2.4 no histórico de 23/11/2026. A capa ainda indica 2.3/Sprint 2. O identificador da issue no backlog não foi localizado. |
| Versão anterior | Validação da implementação sobre `db73ab8b01e355fe5595eeb29df48f6dece83ae5` com as alterações de US16 ainda locais. O resumo original registra `dirty: true`. |
| Versão atual | HEAD local e referência de acompanhamento da branch `feature/US16---Comparar-sequência-manual-e-sequência-sugerida` em `03cffaef12376435d52eaf6da862662a8639c8cd`. Árvore limpa no início e durante os testes oficiais. O diff a partir da base `db73ab8` corresponde aos três commits da US16. [Commit avaliado](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/03cffaef12376435d52eaf6da862662a8639c8cd) · [Diff da US16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/compare/db73ab8...03cffae) |
| PR | Nenhum PR localizado para o head da branch na consulta de 25/11/2026. A CI observada é do evento `push`. |
| Data e ambiente | 25/11/2026, America/Sao_Paulo. Windows, Python 3.11.9, Node 26.13.0, Cypress 16.3.0 e Chrome 158.0.8127.38. FastAPI/Uvicorn e frontend compilado em execução local. PostgreSQL 18.6 em instância dedicada na porta 55438, com bancos distintos para Pytest e Cypress e massa fictícia. |

Este relatório inicia o registro em arquivo da US16. A referência anterior é a validação da implementação registrada na conversa e no resumo do Cypress. A impressão digital dos arquivos de código e teste coletados pelo runner foi a mesma nas duas execuções. O histórico preserva o estado local anterior e a nova execução no commit publicado. [Resumo anterior](evidencias-us16/reavaliacao-03cffae/validacao-implementacao-cypress.json) · [Resumo atual](evidencias-us16/reavaliacao-03cffae/cypress.json)

## 2. Pendências e verificações

| Pendência | Situação anterior | Situação atual | Evidência | Ação restante |
| --- | --- | --- | --- | --- |
| Vincular a validação a um commit ou PR | A execução da implementação registrava o commit base e alterações locais. | **Resolvida e verificada** quanto à versão | O runner registrou o SHA `03cffae`, `dirty: false` e a mesma impressão digital da execução anterior. Os logs da CI mostram checkout do SHA completo. [Resumo local](evidencias-us16/reavaliacao-03cffae/cypress.json) · [CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514) | Conferir a revisão candidata quando houver PR ou alteração de head. |
| Aceite funcional e preservação dos registros | Os três casos já tinham passado na árvore de implementação local. | **Resolvida e verificada** no commit | Três casos aprovados em Chrome local e em Chrome e Electron na CI. [Cenários](../../../frontend/cypress/e2e/comparacao.feature) · [Chrome CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945767) · [Electron CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945860) | Reexecutar após mudanças no fluxo de comparação. |
| Evidência da CI do commit | A conversa anterior registrava apenas a execução local. | **Resolvida e verificada** para o push avaliado | Cinco jobs concluídos com sucesso. Foram conferidos o checkout e a execução dos testes da US16 nos logs de backend e dos dois navegadores. [CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514) | Vincular à execução do PR quando houver integração. |
| Falha do catálogo de máquinas no Planejamento Manual | A revisão da US15 já reproduzia o desaparecimento dos planos quando o catálogo respondia 503. | **Ainda pendente** | No cenário controlado desta revisão, o mesmo defeito impediu usar **Comparar sequências**. A rota da comparação respondeu 200 durante o ensaio. [Revisão da US15](revisao-us15.md) · [JUnit da sondagem](evidencias-us16/reavaliacao-03cffae/sondagem-ui.xml) | Tratar no mesmo registro de defeito do catálogo, caso já esteja acompanhado. Retestar o acesso à comparação após a correção. |
| Integração, DoD vigente, homologação e aceite do PO | A validação da implementação não incluía esses registros. | **Ainda pendente** quanto à integração. **Não foi possível verificar** a DoD formal, a aplicabilidade da homologação e o aceite. | Branch publicada com CI de push. Consulta à API do GitHub pelo head não retornou PR. Os documentos locais atribuem a conferência da DoD ao time e ao PO. [README](../../../README.md) · [Template de PR](../../../.github/pull_request_template.md) | Identificar o PR e a versão vigente da DoD, confirmar a exigência de homologação e obter os registros de integração e aceite. |

## 3. Rastreabilidade

| Critério ou comportamento | Caso de teste | Evidência no commit avaliado | Resultado |
| --- | --- | --- | --- |
| C1 — Exibir plano manual, sugestão e diferenças | **CT-120** | Manual OP01, OP02, OP03 e sugestão OP01, OP03, OP02. A tela indica as duas ordens reposicionadas e mostra 50 min no manual e 20 min na sugerida, diferença de 30 min a menos. O Pytest confirma a seleção da sugestão mais recente entre as que contêm exatamente as ordens do plano. [Cenário](../../../frontend/cypress/e2e/comparacao.feature#L12-L19) · [Integração](../../../backend/testes/integration/test_us16_comparacao.py#L18-L47) | **Aprovado** |
| C2 — Orientar a geração quando falta sugestão | **CT-121** | A interface exibiu «Gere uma sequência sugerida para este planejamento antes de comparar». A API retornou 404 com essa mensagem, a tela não abriu o painel e a contagem de sugestões permaneceu zero. A integração também verificou a existência de uma sugestão de outro conjunto e distinguiu plano inexistente. [Cenário](../../../frontend/cypress/e2e/comparacao.feature#L21-L25) · [Integração](../../../backend/testes/integration/test_us16_comparacao.py#L50-L67) | **Aprovado** |
| A comparação preserva os dados gravados | **CT-122** | O cenário comparou os GETs com os dados retornados na criação do plano e da sugestão e confirmou uma sugestão com três itens persistidos. O teste da API também conferiu que consultar a comparação não alterou registros. [Cenário](../../../frontend/cypress/e2e/comparacao.feature#L27-L34) · [Asserções dos GETs em `03cffae`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/03cffaef12376435d52eaf6da862662a8639c8cd/frontend/cypress/support/step_definitions/sugestao.js#L250-L254) | **Aprovado** |
| Recálculo com plano reordenado e acesso pela API | Testes oficiais de integração, sem ID no plano | A reordenação com duas máquinas produziu setup manual de 30 min e sugerido de 20 min. Remover um tempo de troca necessário retornou `setup: null`, mantendo as duas sequências. A API retornou 401 sem sessão e 403 para Operador autenticado. [Integração](../../../backend/testes/integration/test_us16_comparacao.py#L70-L128) | **Aprovado** |

## 4. Execuções da revisão

| Natureza | Escopo e reprodução | Resultado |
| --- | --- | --- |
| Revisão estática | Compare o HEAD com `db73ab8`. A rota exige perfil `PLANEJADOR`, usa a mesma seleção de sugestão da consulta existente e só lê dados. O recálculo preserva a distribuição por máquina. [Rota](../../../backend/app/api/routes/sugestoes_planejamento.py#L256-L365) · [Cálculo](../../../backend/app/services/sequenciamento_maquinas.py#L7-L22) | Código e asserções conferidos. |
| Pytest local | Dez testes unitários em execução isolada. Cinquenta testes de API em integração com PostgreSQL real, quatro deles específicos de US16. Os bancos novos foram migrados durante a preparação. | **60/60**, 44,19 s. [JUnit local](evidencias-us16/reavaliacao-03cffae/pytest.xml) |
| Cypress local | Chrome 158 com API, frontend e PostgreSQL reais. As interceptações dos casos oficiais observam as respostas. | **15/15**, 74,94 s. Três da US16, cinco da US15, quatro da matriz de setup, duas variantes do CT-115 e CT-110. [Resumo local](evidencias-us16/reavaliacao-03cffae/cypress.json) |
| Sondagem de QA | Cypress com serviços reais e injeção de 503 em apenas `GET /api/maquinas`. Execução separada em `.tmp/qa-us16-review/catalogo-sondagem.cy.js`. | **1 reprodução confirmada**, 3,57 s. A asserção do ensaio verifica a ocorrência do defeito. [JUnit da sondagem](evidencias-us16/reavaliacao-03cffae/sondagem-ui.xml) |
| CI de push do SHA avaliado | Ubuntu, PostgreSQL 18, Pytest completo e Cypress com `npm run test:e2e:regressao` em cada navegador. Os logs do checkout apontam para `03cffaef12376435d52eaf6da862662a8639c8cd`. O nome do job de aceite é antigo e a execução inclui `comparacao.feature`. | **253/253** no [backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945702), **63/63** no [Chrome 157](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945767) e **63/63** no [Electron 150](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945860), com os três casos da US16 nos dois. O [job de lint e build](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514/job/139575945819) também passou. |

No backend, configure `TEST_DATABASE_URL` com um banco descartável terminado em `_test`. Execute a partir de `backend`.

```powershell
python -m pytest -q --junitxml=pytest-us16.xml testes/integration/test_us12_planejamento_manual.py testes/integration/test_us13_sequencia_sugerida.py testes/integration/test_us14_prazos_prioridades.py testes/integration/test_us15_compatibilidade.py testes/integration/test_us16_comparacao.py testes/unit/test_us15_sequenciamento.py
```

No navegador, prepare outro PostgreSQL terminado em `_e2e_test`. Aplique `alembic upgrade head` e inicie a API e o frontend seguindo o [guia do Cypress](../../../frontend/cypress/README.md). A regressão direcionada foi executada a partir de `frontend`.

```powershell
npm run test:e2e -- --browser chrome --tags '(@US11 or @CT110 or @CT115 or @US15 or @US16) and not @wip'
```

## 5. Defeito confirmado

### Erro no catálogo de máquinas impede abrir a comparação pela interface

É uma regressão já registrada na revisão da US15. O impacto sobre a ação **Comparar sequências** foi confirmado nesta avaliação. A severidade sugerida é **média**. O Planejador perde o acesso ao fluxo quando o catálogo está indisponível e os dados continuam consultáveis pela API. [Registro original](revisao-us15.md) · [Carregamento conjunto em `03cffae`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/03cffaef12376435d52eaf6da862662a8639c8cd/frontend/src/features/planejamentos/pages/PlanejamentosPage.tsx#L51-L83)

1. Com uma conta Planejador, salve um planejamento para a ordem fictícia OP01 e gere uma sugestão correspondente. Abra **Planejamento manual** e confirme a comparação com os serviços saudáveis. [Captura do controle](evidencias-us16/reavaliacao-03cffae/comparacao-com-catalogo-disponivel.png)
2. No navegador, substitua somente a resposta de `GET /api/maquinas` por HTTP 503. Recarregue e reabra **Planejamento manual**.
3. Confirme os HTTP 200 de `GET /api/ordens-producao` e `GET /api/planejamentos`, com o plano no corpo deste último. Consulte `GET /api/planejamentos/{id}/comparacao` na mesma sessão.

**Resultado esperado para a correção.** Os planos recebidos com HTTP 200 permanecem visíveis, a comparação pode ser aberta no cartão e a falha é indicada junto ao catálogo.

**Resultado obtido.** A tela exibiu «Não foi possível carregar os dados» e ocultou o cartão e o botão de comparação. A consulta direta da comparação devolveu HTTP 200 com o plano e a sugestão. O reteste usou uma resposta 503 injetada em laboratório. [Captura com 503](evidencias-us16/reavaliacao-03cffae/cartao-ausente-com-catalogo-503.png) · [JUnit da sondagem](evidencias-us16/reavaliacao-03cffae/sondagem-ui.xml)

## 6. DoD na avaliação de `03cffae`

DoD formal da US16 — **Não verificado**. A tabela registra as condições observáveis do plano, do template de PR e da revisão. A release pode ter outras condições acordadas pela equipe.

| Condição | Estado | Evidência ou dependência |
| --- | --- | --- |
| Revisão de QA e integração via PR | **Não atendido** | A revisão local está registrada. A consulta à branch no GitHub não identificou PR e a referência local de `origin/main` estava em `db73ab8`. |
| Critérios de aceite validados | **Atendido** | C1 e C2 passaram nas condições do plano. CT-122 também passou. A regressão em condição de indisponibilidade consta na seção 5. |
| Testes escritos e passando | **Atendido** | Há quatro testes de integração da US16 e três cenários Cypress, todos executados com sucesso. |
| CI sem falhas na versão avaliada | **Atendido** | Os cinco jobs da [CI do push](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45720091514) terminaram com sucesso para o SHA avaliado. |
| Documentação da entrega | **Atendido** no escopo consultado | O guia de backend descreve API, seleção da sugestão e decisão de recálculo. O guia Cypress lista os casos do plano. [Backend](../../../backend/README.md#us16--comparação-de-sequências) · [Cypress](../../../frontend/cypress/README.md#cenários-da-us16) |
| Homologação quando exigida | **Não verificado** | Falta confirmar se a release exige homologação e identificar a revisão implantada. Quando aplicável, executar CT-120, CT-121 e CT-122 com dados de teste e anexar o resultado ao PR. |
| Aceite do PO | **Não verificado** | Falta o registro de aceite da história pelo PO. |

## 7. Reteste e regressão

- **Reteste da pendência anterior.** A falha do catálogo voltou a ocorrer, agora com um plano que já possuía uma sugestão. Para encerrar o defeito, repita o controle com resposta normal, injete somente o 503 do catálogo e confira o cartão, o painel de comparação e o aviso da dependência. Restaure o catálogo e confira a exibição da máquina e dos setups.
- **Regressão da versão.** O Pytest cobriu gravação e edição de planos da US12, geração e consulta da US13, prazos e prioridades da US14 e compatibilidade da US15. No navegador, CT-110 verifica recuperar a sugestão com o plano preservado, CT-115 exercita as regras de urgência no mesmo fluxo, a US15 confere as máquinas atribuídas e a US11 verifica os dados direcionais de setup consumidos pela comparação. O cenário `US15_CT05` também passou para a distribuição alternativa com setup ausente. [Resultados locais](evidencias-us16/reavaliacao-03cffae/cypress.json)
- **Resumo quantitativo.** Três casos do plano da US16, com três aprovados, incluindo CT-122 de regressão. A execução local abrangeu 15 cenários no navegador e 60 testes de backend. As suítes da CI e a sondagem estão registradas por execução. Os três casos do plano foram contados uma vez, mesmo com execuções em ambientes diferentes.

## 8. Limitações e ações restantes

- Confirmar a issue da US16 no backlog, o texto vigente da DoD e a situação da integração. A evidência de CI disponível é do push da branch.
- Confirmar se a release exige homologação. Quando exigida, identificar a revisão implantada e executar os três casos do plano no ambiente de destino.
- Registrar o tratamento da regressão do catálogo e o aceite formal pelo PO. O resultado do 503 refere-se à resposta simulada no navegador.

## 9. Histórico e parecer

| Data | Versão | Registro |
| --- | --- | --- |
| 25/11/2026 | `db73ab8` com alterações locais da US16 | A primeira tentativa de Pytest registrou um erro de preparação no teste novo, que usava o nome incorreto de uma tabela. A primeira tentativa de Cypress foi interrompida durante a gravação e ficou sem resultado do runner. Após correção do teste e nova execução sem vídeo, passaram 253 testes de backend e 31 casos Cypress, incluindo CT-120, CT-121 e CT-122. [Resumo da implementação](evidencias-us16/reavaliacao-03cffae/validacao-implementacao-cypress.json) |
| 25/11/2026 | `03cffaef12376435d52eaf6da862662a8639c8cd` | Reexecução com a árvore limpa. 60 Pytest e 15 Cypress locais passaram. A CI do commit passou no backend e nos dois navegadores. O reteste do catálogo confirmou a perda de acesso à comparação pela interface durante 503. |
| 25/11/2026 | `1e98b763e7fedfe195f4d9c1dd3f95665187bea9` | Corrigido o bloqueio da interface durante o 503. O cenário novo reprovou antes da correção e passou depois. A regressão teve 31 aprovações e o CT-85 passou em reexecução isolada após a falha de ambiente. |

**Parecer em `03cffae` — Validação inconclusiva para aceite.** Os critérios fornecidos e a preservação dos registros foram comprovados nas condições do plano. O defeito de catálogo seguia reproduzível, com impacto confirmado na comparação. A conclusão dependia do tratamento desse defeito, da verificação da DoD vigente, da integração via PR e das evidências de homologação quando exigida e de aceite pelo PO.
