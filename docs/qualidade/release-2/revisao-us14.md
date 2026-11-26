# Revisão de QA da US-14 — Prazos e prioridades no sequenciamento

**Situação da entrega em 26/11/2026 · Aprovada pelo PO e integrada à `main`.** [PR #23](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/23) (`39ab129`). Os sete critérios do DoD estão concluídos para o incremento aceito. [Definition of Done](../../status-projeto.md#definition-of-done-dod)

A reavaliação documenta a regra de sequenciamento aprovada e os testes no Chrome e no Electron. A reversão da migração com dados permanece como risco operacional. [Auditoria integrada](auditoria-bugs/relatorio-validacao.md#6-suspeitas-lacunas-e-riscos-operacionais)

As seções 1 a 9 preservam a revisão do commit `879a025`. A [reavaliação após a decisão do PO](#reavaliação-após-a-decisão-do-po) registra a aplicação da regra e o novo reteste.

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Projeto e item | SetupFlow, US-14 — Considerar prazos e prioridades no sequenciamento. História funcional para o perfil Planejador de Produção. |
| Issue | [SC-31 no Jira](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-31), vinculada no PR. |
| PR e autor | [PR #23](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/23), Luiz Inácio Moura da Costa (`@luizmouradc`). Aberto e sem merge na consulta. |
| Release e sprint | Release 2 / Sprint 3 |
| Branch e commit local | `feature/us14-prazos-prioridades`, [`879a025043a636bc8ab6f4088e902268cdeb294a`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/879a025043a636bc8ab6f4088e902268cdeb294a). Árvore limpa antes da revisão. |
| Base e commit executado na CI | `main` em `e5d73f1d473892bd883faf49ba87c31f62c88948`. O checkout da CI usou o merge de teste `8dc9e15e6a8b5f029e16a782bbed9ce5d8d1513c`, que combina o head avaliado com essa base. [CI #154](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426) |
| Ambiente | Local em Windows, Python 3.11.9, Pytest 8.4.2, FastAPI 0.162.0 e PostgreSQL 18.6 em instância dedicada de loopback. CI em Ubuntu com Python 3.11, Node 22, PostgreSQL 18 e Cypress 16.3.0, Chrome 157 e Electron 150 headless. |
| Data da avaliação | 25/11/2026, America/Sao_Paulo |

Foram consultados os READMEs, templates de PR e US, workflow, mudanças a partir de `main`, testes e evidências do autor. A busca no repositório e nos diretórios ancestrais consultados não encontrou `AGENTS.md`. A matriz da Sprint 3 do anexo `Plano-de-Teste-SetupFlow-3.md` é a referência de cobertura. Seu histórico registra a versão 2.4, de 23/11/2026, e sua identificação de capa ainda indica 2.3/Sprint 2. O plano de qualidade remete os critérios de aceite ao backlog e a DoD aos acordos da equipe. A consulta sem autenticação à SC-31 retornou HTTP 404 e a integração Atlassian estava indisponível nesta sessão. O conteúdo integral da issue e os acordos vigentes ficaram sem verificação. [Plano de qualidade, aba Orientações, C8](../Plano-de-Qualidade-SetupFlow.xlsx) · [Relatório de testes do autor](../../releases/release2/sprint3/relatorio-testes-us14.md)

## 2. Parecer resumido e principais pendências

**Pendente de ajustes.** Os casos automatizados de prazo, prioridade, urgência com aumento de setup e dados incompletos passaram. A geração sem dados de urgência, a persistência e as permissões da API também foram verificadas. A CI executou a US-14 em Chrome e Electron.

- **Regra de aceite pendente.** No conflito do CT-115, a API colocou a ordem de prioridade Baixa primeiro quando isso evitou um atraso. Ao relaxar seu prazo, a ordem de prioridade Alta passou para a primeira posição. A resposta esperada para esse conflito e para o desempate pelo setup depende da decisão do PO.
- **Rollback reproduzido.** Uma sugestão válida, com setup de 5 para 30 minutos, impediu o downgrade para a revisão anterior do banco. A transação preservou os dados e a revisão atual. O risco já está descrito pelo autor.
- **DoD em aberto.** A integração via PR ainda está pendente. A definição formal, o aceite do PO e a exigência ou evidência de homologação também precisam ser confirmados.

## 3. Rastreabilidade

C1 e C2 são referências da matriz do plano anexado. `US14_CT01–04` são as tags existentes no Cypress. Os resultados abaixo registram o que foi comprovado no comportamento atual e identificam onde falta o resultado esperado pelo PO.

| Critério ou comportamento | Caso de teste | Evidência | Resultado |
| --- | --- | --- | --- |
| C1, influência isolada do prazo | **CT-113**, variante de prazo. `US14_CT02` e `test_prazo_influencia_ordens_de_mesma_prioridade`. | Com mesma prioridade e setup zero, a ordem de prazo anterior veio primeiro. A sondagem local com famílias distintas, ambos os prazos viáveis e setups de 5/30 min escolheu a sequência de 5 min, deixando o prazo anterior em segundo. [Integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/testes/integration/test_us14_prazos_prioridades.py#L109-L117) · [Cypress](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/frontend/cypress/e2e/prazos-prioridades.feature#L22-L28) | **Aprovado no cenário nominal.** Resultado esperado do desempate aguarda PO. |
| C1, influência isolada da prioridade | **CT-113**, variante de prioridade. `US14_CT03`, `test_prioridade_influencia_ordens_de_mesmo_prazo` e `test_prioridade_influencia_sem_risco_de_atraso`. | Com prazo e duração iguais, Alta veio antes de Baixa. [Integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/testes/integration/test_us14_prazos_prioridades.py#L120-L128) · [Cypress](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/frontend/cypress/e2e/prazos-prioridades.feature#L30-L36) | **Aprovado no cenário executado.** |
| C2, ordem de prioridade alta com prazo restritivo e preservação das restrições | **CT-114**. `US14_CT01` e `test_ordem_prioritaria_com_prazo_restritivo`. | Com início fixado às 23h, ordem Alta de 40 min foi antecipada para evitar atraso, elevando o setup de 5 para 30 min. POST 201, 1 sugestão e 3 itens, posições e setups conferidos e GET igual ao POST. No Cypress, com prazo de dois dias, foram verificados ordem, setup e gravação. [Integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/testes/integration/test_us14_prazos_prioridades.py#L86-L106) · [Cypress](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/frontend/cypress/e2e/prazos-prioridades.feature#L11-L20) | **Aprovado no cenário executado.** O risco efetivo de atraso foi exercitado com relógio controlado no backend. |
| Precedência entre prazo anterior, prioridade maior e setup menor | **CT-115**. Sondagem de QA realizada pela API. O teste unitário existente `test_prazo_restritivo_pode_antecipar_ordem_de_prioridade_baixa` usa a mesma família e não cobre setup distinto. | Com início às 23h, 40 min por ordem e setup A→B/B→A de 5/30 min, o prazo mais restritivo fez B/Baixa vir primeiro. Com prazo relaxado, A/Alta veio primeiro. [Critérios de pontuação](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/app/services/sequenciamento.py#L131-L177) | **Executado, aceite bloqueado.** Precedência esperada aguarda PO. |
| Dados incompletos no fluxo com urgência | Casos complementares `US14_CT04`, `test_dados_incompletos_impedem_persistencia` e `test_duracao_ausente_impede_persistencia`. | POST 422, mensagem por ordem e campo, zero sugestões e zero itens. O Cypress verifica alerta na tela e ausência do painel. [Validação da API](../../../backend/app/api/routes/sugestoes_planejamento.py#L91-L139) · [Cypress](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/frontend/cypress/e2e/prazos-prioridades.feature#L36-L44) | **Aprovado.** O comportamento é descrito pelo PR. |
| Seleção e setup direcional da US13, acesso de Planejador e ausência de regressão | `test_sem_dados_de_urgencia_preserva_us13`, suíte backend US13 e Cypress `@CT85` para o Operador. | Redução por setup sem prazo/prioridade, recuperação e persistência. API exige sessão e perfil, com 401 sem sessão no POST e 403 para Operador no POST e nas duas consultas. [Testes US13](../../../backend/testes/integration/test_us13_sequencia_sugerida.py#L64) · [Proteção da API](../../../backend/testes/integration/test_us13_sequencia_sugerida.py#L215-L222) | **Aprovado na regressão executada.** |

O sequenciamento usa duração estimada e setup acumulado para calcular o atraso em relação ao fim do dia, tomando o início em `America/Recife`. Classifica as alternativas por total de ordens atrasadas, depois por atrasos por prioridade. Entre outros desempates, usa inversões de prioridade, total de setup e inversões de prazo, nessa ordem. A escolha é feita entre as alternativas que a heurística gera. [Serviço de sequenciamento](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/app/services/sequenciamento.py#L61-L183) · [Início usado pela API](../../../backend/app/api/routes/sugestoes_planejamento.py#L135-L140)

## 4. Testes executados e resultados

| Método | Execução e evidência | Resultado |
| --- | --- | --- |
| Revisão estática | `git diff --check origin/main...HEAD`, leitura do diff, algoritmo, rotas, migration, testes e configuração da CI. | Diff sem erros de whitespace. |
| Ensaio isolado da lógica | Quatro unitários da US-14 em `test_us14_sequenciamento.py`. Também coletados na suíte completa. Ensaio adicional chamou o serviço diretamente, com início às 23h, mesma família, A/Alta de 40 min com prazo amanhã e B/Baixa com prazo hoje. | 4/4 unitários localmente e 4/4 na CI. No ensaio de limite, o serviço devolveu A→B com B de 20 min, terminando exatamente à meia-noite, e B→A com B de 21 min. Essa observação descreve o limite usado pelo código. |
| Integração em processo, API FastAPI e banco real | Pytest/TestClient contra PostgreSQL isolado, com Alembic até `6b14a2e9c703`. Os cinco testes oficiais da US-14 controlam o início da simulação com `monkeypatch`. | **222/222 localmente em 204,09 s** no head e **222/222 na CI**, incluindo 5/5 integrações US-14 e 4/4 unitários US-14. [Log do job Backend pytest](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/job/139340666420) |
| Sondagens temporárias de QA, API em processo e banco real | `test_sondagem_us14.py`, arquivo temporário executado com `python -m pytest -s -q`. Usou TestClient, os dados da seção 5, relógio da API fixado em 23h e banco `qa_us14_migration_test`. | **3/3 sondagens reproduziram a observação, em 9,83 s.** As asserções fixam o comportamento observado, inclusive a exceção do downgrade. |
| Integração ponta a ponta na CI | `alembic upgrade head`, API Uvicorn, frontend real, PostgreSQL exclusivo e Cypress. O `cy.intercept` nos passos de geração observa o POST e a resposta real. | Chrome **53/53**, incluindo **4/4 US-14**. Electron **53/53**, incluindo **4/4 US-14**. [Log Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/job/139340666484) · [Log Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/job/139340666472) |
| Cypress de login com respostas simuladas | Job separado de login, Chrome, `cypress.config.ts`. Aprovado no seu próprio escopo. | **12/12**. [Log do Cypress de login](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/job/139340666129) |
| Verificação de frontend na CI | `npm run lint` e `npm run build`. | Ambos passaram. [Log do job](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/job/139340666483) |

A CI executa `python -m pytest -v --junitxml=junit.xml testes` e `npm run test:e2e:regressao -- --browser <chrome|electron>`. A feature US-14 herda `@regressao` e o US14_CT01 também tem `@smoke`. Apesar do nome do job mencionar US11, US13 e US32, os logs mostram os quatro cenários US-14 nos dois navegadores. Os artefatos associam o run ao head `879a025` e os logs registram o checkout do merge de teste. [Workflow](../../../.github/workflows/ci.yml#L76-L145) · [Filtro de regressão](../../../frontend/package.json#L11-L15) · [JUnit do backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/artifacts/15041742031) · [Artefatos Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/artifacts/15041807325) · [Artefatos Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426/artifacts/15041922097)

Comandos de reprodução da suíte no head, com dependências de `backend/requirements.txt` e `TEST_DATABASE_URL` apontando para um PostgreSQL de teste dedicado com sufixo `_test`.

```powershell
# Na raiz
git rev-parse HEAD
git diff --check origin/main...HEAD
Set-Location backend
python -m pytest -q testes/unit/test_us14_sequenciamento.py
python -m pytest -v testes/integration/test_us14_prazos_prioridades.py testes/integration/test_us13_sequencia_sugerida.py
python -m pytest -q --junitxml=qa-us14-pytest.xml testes
```

Para repetir o E2E, prepare um banco distinto com sufixo `_e2e_test`, aplique as migrations e inicie os serviços seguindo o guia do Cypress. Execute os comandos a partir de `frontend` com `E2E_DATABASE_URL` configurada.

```powershell
npm run test:e2e -- --browser chrome --tags "@US14 and not @wip"
npm run test:e2e -- --browser electron --tags "@US14 and not @wip"
npm run test:e2e:regressao -- --browser chrome
npm run test:e2e:regressao -- --browser electron
```

[Configuração local e requisitos do E2E](../../../frontend/cypress/README.md#L12)

## 5. Bugs e pendências

### Downgrade falha após gravar sugestão válida com aumento de setup

- **Classificação e severidade sugerida.** Bug operacional confirmado, **média**. Bloqueia a reversão simples do esquema com dados válidos da US-14. O upgrade e a geração normal passaram. A severidade deve ser revista se o plano de implantação depender desse downgrade.
- **Comportamento afetado.** Retorno à revisão da US13. O downgrade recria a restrição que exige setup total menor ou igual ao original. O PR e a documentação já registram a limitação. [Migration](../../../backend/migrations/versions/6b14a2e9c703_permite_setup_maior_us14.py#L25-L36) · [Modelo de dados](../../arquitetura/modelo-de-dados.md#L194)
- **Pré-condições e passos.** Use um banco descartável em `6b14a2e9c703`. Gere pela API uma sugestão com setup original de 5 min e sugerido de 30 min. O teste oficial `test_ordem_prioritaria_com_prazo_restritivo` pode preparar os dados se executado sozinho nesse banco. Aponte as variáveis `DB_*` do Alembic para o mesmo banco, execute `python -m alembic downgrade 13e41f6d48c2` e confira `SELECT version_num FROM alembic_version` e a sugestão gravada.
- **Esperado para um rollback operacional.** Voltar à versão suportada com tratamento explícito para preservar os registros incompatíveis, ou executar o procedimento alternativo de reversão acordado.
- **Obtido.** PostgreSQL rejeitou `ck_sugestao_planejamento_tempos` com SQLSTATE `23514`. Após o rollback da transação de DDL, a versão continuou `6b14a2e9c703` e a sugestão permaneceu gravada. A sondagem foi feita com Alembic e banco real local, em dados fictícios.
- **Critério de encerramento proposto.** **Dado** um banco com sugestão US-14 de setup 30/5, **quando** a equipe executar o procedimento de reversão adotado em banco de teste, **então** a versão anterior deve voltar a operar e a sugestão deve receber o tratamento de preservação acordado e verificável.

### Precedência entre prazo, prioridade e setup ainda sem resultado esperado aprovado

- **Classificação e impacto.** Suspeita a validar. **Impacto potencial médio** se a precedência divergir da regra do PO, pois muda a ordem de trabalho recomendada. A divergência funcional ainda não está estabelecida.
- **Critério e código.** CT-115 e desempate do CT-113. [Pontuação e ordenação de alternativas](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/879a025043a636bc8ab6f4088e902268cdeb294a/backend/app/services/sequenciamento.py#L131-L177)
- **Pré-condições e passos.** Use duas ordens pendentes de 40 min em famílias diferentes, com A→B = 5 min e B→A = 30 min. Fixe o relógio da rota de geração em 23h, como no fixture `cenario_us14`. Defina a ordem A como Alta, prazo amanhã, e B como Baixa, prazo hoje. Gere para `[A, B]`, relaxe o prazo de B para amanhã e gere novamente. Para o desempate, use prioridade Média nas duas ordens, prazo de A depois do de B e espaço para concluir ambas em qualquer sequência.
- **Esperado.** A sequência escolhida e a ordem de desempate devem seguir a regra a confirmar pelo PO. **Obtido.** Primeiro cenário, HTTP 201, B→A, setup 30 min. Controle com prazo relaxado, HTTP 201, A→B, setup 5 min. No desempate, A→B e setup 5 min, apesar de B ter prazo anterior. Sondagens realizadas por TestClient com PostgreSQL e relógio controlado.
- **Critério de encerramento.** **Dado** que o PO registrou a precedência e os desempates, **quando** os mesmos dados forem exercitados na API e no fluxo do Planejador, **então** sequência, setup, ausência de duplicação de itens e resultado de cada variante devem corresponder à regra aprovada e ficar vinculados ao CT-115 e ao CT-113.

### Evidência anterior e documentação de CI precisam de atualização

- **Classificação e impacto.** Melhoria de rastreabilidade, **impacto baixo**. Os logs atuais da CI já comprovam a execução no commit de teste do PR.
- **Passos e evidência.** Abra os dois resumos Chrome anexados pelo autor e compare `commit` e `dirty`. Ambos registram `e5d73f1` e `dirty: true`. Compare também os arquivos `US14_CT02.png` e `US14_CT03.png` com `Get-FileHash -Algorithm SHA256`. Têm os mesmos bytes, coerentes com telas que mostram a mesma sequência e setup. A captura sozinha não distingue os dados de entrada. O README do Cypress ainda indica a execução na CI como pendente de confirmação. [Resumo US14](../../releases/release2/sprint3/evidencias/us14/chrome-us14-resumo.json) · [Resumo de regressão](../../releases/release2/sprint3/evidencias/us14/chrome-regressao-resumo.json) · [Guia Cypress](../../../frontend/cypress/README.md#L166-L169)
- **Esperado e critério de encerramento.** Vincular os casos e as variantes de entrada aos logs, resultados e revisão testada. Atualizar o guia com o run que executou os casos nos dois navegadores.

**Acompanhamento.** A busca nas issues abertas e fechadas por US14, US-14, SC-31, sequenciamento e migration não encontrou registro equivalente. As issues de regressão [#18, US11](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) e [#19, Driver06](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19) estavam fechadas e descrevem outros comportamentos. O downgrade já consta no PR #23. Use esse registro para acompanhar o risco e verifique a SC-31 antes de registrar eventual issue separada.

## 6. DoD na avaliação de `879a025`

**DoD formal vigente da SC-31 — Não verificado.** A tabela avalia cada condição publicada na seção 7 do [relatório do item](../../releases/release2/sprint3/relatorio-testes-us14.md#L129), à luz da seção 7 do plano anexado e dos resultados auditados.

| Critério disponível | Estado | Evidência ou pendência |
| --- | --- | --- |
| Implementação da história | **Não verificado** | Entrega da API e interface exercitada. A conformidade integral depende dos critérios oficiais e da decisão para o CT-115 e desempate do CT-113. |
| Testes automatizados escritos e aprovados | **Atendido** | Os 9 testes backend da US-14 e os 4 cenários Cypress existentes passaram na CI. A conclusão dos casos planejados continua condicionada à regra do PO. |
| Validação funcional local | **Atendido** | TestClient com PostgreSQL local e sondagens da seção 4. O E2E com navegador foi conferido na CI. |
| Evidências registradas | **Atendido** | Logs da CI vinculam o PR, o head, o merge de teste e os casos. A seção 5 registra as limitações da evidência anterior. |
| Documentação técnica atualizada | **Atendido** | Alterações de algoritmo, API, migration, restrições e guia de teste documentadas. Resta atualizar a referência histórica ao estado da CI. [Backend](../../../backend/README.md#L198) · [Modelo de dados](../../arquitetura/modelo-de-dados.md#L182) |
| Revisão e integração via Pull Request | **Não atendido** | Revisão de QA registrada. PR #23 aberto e sem merge quando consultado. [PR #23](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/23) |
| Pipeline de CI sem falhas | **Atendido** | Cinco jobs aprovados na execução do PR. A regressão pelo filtro `@regressao` incluiu o cenário marcado como smoke da US-14. [CI #154](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45652571426) |
| Homologação, quando exigida | **Não verificado** | Exigência para esta história, URL, versão implantada e evidência do ambiente não confirmadas. |
| Aceite do PO | **Não verificado** | Pendente de decisão e registro pelo PO. |

Para o encerramento dos testes deste item conforme o plano, as execuções e a regressão estão registradas. O resultado esperado de CT-115 e o desempate de CT-113 seguem pendentes, portanto a cobertura de aceite da US-14 permanece incompleta. A conclusão da Sprint 3 depende da avaliação dos demais itens da release.

## 7. Reteste e regressão

- **Reteste da mudança de banco no PR.** A migração subiu até `6b14a2e9c703` e o caso de aumento de setup gravou e recuperou os itens. Isso recompõe o cenário que a restrição antiga impedia. O downgrade foi exercitado separadamente e permanece como pendência operacional. Após haver um procedimento de reversão, repetir com sugestão 30/5 em banco descartável e verificar versão, registros e funcionamento da versão restaurada.
- **Reteste funcional após decisão do PO.** Executar CT-115 com prazo restritivo e controle, e CT-113 com mesma prioridade e setup assimétrico. Assegurar prazo inicial, duração, tempos direcionais, resultado da API e sequência apresentada na tela. Manter a variante do CT-114 que faz a sequência alternativa evitar atraso e o caso incompleto que retorna 422 sem gravar.
- **Regressão executada.** Pytest completo. US07–09 alimentam a sugestão com ordens, prazo, prioridade e duração. US10–11 fornecem e exibem setup. US12–13 compartilham seleção, planejamento manual, geração e consulta de sugestão. A CI também executou o gerenciamento US32, além do login em job separado. O navegador exercitou 4 cenários de matriz, 13 de sequência sugerida, 4 de prazos/prioridades e 32 de usuários em cada navegador. Verificar novamente após alteração do algoritmo ou da migration.
- **Bugs anteriores.** A regressão geral passou nos casos executados. Os roteiros específicos de reprodução das issues #18 e #19, com respostas simuladas, não foram reexecutados nesta avaliação. Se uma release candidata incorporar correções desses itens, use os retestes já vinculados às respectivas issues.

## 8. Limitações da avaliação e ações pendentes

| Pendente | Ação para encerrar |
| --- | --- |
| SC-31 e acordo vigente da equipe | Obter o conteúdo da issue e a versão da DoD acordada. Confirmar C1/C2, obrigatoriedade dos dados incompletos e exigência de homologação. |
| Resultado esperado de CT-115 e desempate de CT-113 | Registrar a decisão do PO e repetir as variantes da seção 5. O caso adicional no navegador depende dessa decisão e pode ser reproduzido preparando os mesmos dados por API e acionando **Gerar sequência sugerida** na tela de Planejamentos. |
| Reversão do banco | Definir com DevOps o procedimento para sugestões US-14 já gravadas. Ensaiá-lo com o roteiro da seção 5 e anexar o resultado ao registro da implantação. |
| Homologação e integração | Quando aplicável, identificar o commit implantado e repetir os fluxos principal, negativo e de perfil com dados de teste. Registrar a revisão e integração do PR e validar a versão candidata. |

## 9. Parecer de QA da avaliação original

**Pendente de ajustes.** A automação do PR #23 passou, inclusive a persistência de sugestões com setup maior. O CT-115 foi exercitado e aguarda confirmação da regra esperada. A falha de downgrade foi reproduzida, e a integração via PR continua pendente. A conclusão do aceite exige comprovar os critérios oficiais da SC-31 e a DoD aplicável. O parecer de QA não substitui o aceite do PO.

### Comentário da revisão original

> QA no commit `879a025043a636bc8ab6f4088e902268cdeb294a`. A CI passou 222 testes de backend e 53 cenários em cada navegador, incluindo os quatro da US-14. Reproduzi o conflito prazo × prioridade × setup do CT-115, cujo resultado esperado aguarda decisão do PO, e confirmei que o downgrade falha após gravar uma sugestão de setup 30/5. A DoD formal e a integração do PR seguem pendentes. **Parecer de QA: Pendente de ajustes.** Relatório: [inserir link].

## Reavaliação após a decisão do PO

Em 25/11/2026, o QA informou a aprovação do PO para a regra de sequenciamento. A sequência de referência segue **Alta → Média → Baixa**. Dentro da mesma prioridade, vem primeiro o prazo mais próximo. Com prioridade e prazo iguais, vence o menor setup total entre as alternativas avaliadas. Uma ordem de prioridade menor pode passar à frente se chegar a tempo e preservar o prazo ou o atraso de cada ordem mais prioritária. [Serviço](../../../backend/app/services/sequenciamento.py) · [Guia do backend](../../../backend/README.md#regras-de-sequenciamento)

| Reteste | Dados e resultado esperado | Automação |
| --- | --- | --- |
| CT-113, prazo antes de setup | Mesma prioridade, prazos diferentes e ambos viáveis. A ordem de prazo anterior vem primeiro, mesmo ao elevar o setup de 5 para 30 min. | [Pytest de integração](../../../backend/testes/integration/test_us14_prazos_prioridades.py) e [Cypress `US14_CT02`](../../../frontend/cypress/e2e/prazos-prioridades.feature) |
| CT-113, desempate pelo setup | Prioridade e prazo iguais. A sequência de 5 min vence a de 30 min. | [Pytest de integração](../../../backend/testes/integration/test_us14_prazos_prioridades.py) |
| CT-115, conflito e controle | Com Baixa em risco, Baixa → Alta e setup de 30 min. Com ambos os prazos viáveis, Alta → Baixa e setup de 5 min. Cada cenário grava uma sugestão com duas ordens. | [Pytest de integração](../../../backend/testes/integration/test_us14_prazos_prioridades.py) e [Cypress `@CT115`](../../../frontend/cypress/e2e/prazos-prioridades.feature) |
| Proteção da ordem Alta | Preservar Alta em primeiro se antecipar Baixa causaria ou agravaria o atraso da Alta. Antecipar apenas a Baixa que pode cumprir seu prazo quando a janela comporta uma única ordem. | [Pytest unitário](../../../backend/testes/unit/test_us14_sequenciamento.py) |

**Resultado do backend local.** `python -m pytest -q --junitxml=pytest-final.xml testes` registrou **229 aprovados em 305,93 s**, com 7 unitários e 9 testes de integração da US-14 incluídos no total. As integrações usaram TestClient e PostgreSQL 18.6 isolado, com relógio controlado nos testes da história. Um ensaio adicional executou 1.000 conjuntos sintéticos de uma família para conferir a ordem de prazo dentro de cada prioridade e a proteção individual durante antecipações. O lint e o build do frontend também passaram.

**Resultado de navegador local.** O Cypress 16.3.0 registrou **6/6 aprovados no Chrome 158.0.8127.38** e **6/6 no Electron 150.0.7871.250**, incluindo os dois exemplos do CT-115. A execução usou o frontend compilado, a API real e outro banco PostgreSQL isolado. O comando foi `npm run test:e2e -- --browser chrome --tags "@US14 and not @wip"`, repetido com `--browser electron`. Os dois resumos registraram o mesmo hash das fontes testadas, `93a2f2f87f01153eff565775a62610bd28e70534020bf2be5654c615ba4af297`.

**Risco operacional registrado.** O downgrade descrito na revisão original segue em aberto. A execução de CI citada nas seções anteriores corresponde àquela revisão.
