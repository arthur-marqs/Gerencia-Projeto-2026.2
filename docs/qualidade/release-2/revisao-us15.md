# Revisão de QA da US-15 — Compatibilidade entre produtos e máquinas no sequenciamento

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Projeto e item | SetupFlow, US-15 — Considerar compatibilidade entre produtos e máquinas no sequenciamento. Perfil Planejador de Produção. |
| Issue | [SC-32 no Jira](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-32) |
| PR e autor | [PR #24](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24), Luiz Inácio Moura da Costa (`@luizmouradc`). Aberto e sem merge na consulta. |
| Release e sprint | Release 2 / Sprint 3 |
| Branch e versão avaliada | `feature/SC-32-us15-compatibilidade-sequenciamento`, [`ca23d0f4e775719c40926f1de12d3b7d6b096a93`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/ca23d0f4e775719c40926f1de12d3b7d6b096a93). A árvore de código local estava limpa no início da revisão. |
| CI | [Execução #159](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438), vinculada ao head acima. Os jobs executaram o merge de teste `1ca7ce672056ad834cf5ccf1e679763c13fcce26` com a base `main` em `39ab1296c3e52a7a5ee04c104bc3a6bd32c051fe`, que inclui o PR #23 da US-14. |
| Ambiente local | Windows, Python 3.11.9, Pytest 8.4.2, PostgreSQL 18.6 em instância descartável de loopback, Node 26.13.0 e Cypress 16.3.0 com Chrome 158.0.8127.38. |
| Data | 25/11/2026, America/Sao_Paulo |

Os critérios e os sete itens da DoD fornecidos pelo QA serviram de referência. Foram consultados o README, os guias do backend e do Cypress, a configuração da CI, a documentação técnica e o diff. A busca por `AGENTS.md` no repositório e nos ancestrais consultados não encontrou instruções. O histórico do plano anexado `Plano-de-Teste-SetupFlow-3.md` registra a revisão 2.4 para a Sprint 3, com CT-116 a CT-119. A capa ainda indica 2.3/Sprint 2. O plano de qualidade remete critérios ao backlog e DoD aos acordos da equipe. A consulta pública à SC-32 ficou indisponível e o endpoint do Jira sem autenticação retornou HTTP 404. [Plano de qualidade, aba Orientações, C8](../Plano-de-Qualidade-SetupFlow.xlsx) · [Relatório do autor](../../releases/release2/sprint3/relatorio-testes-us15.md)

## 2. Parecer resumido e principais pendências

**Pendente de ajustes.** Nos cenários nominais, a API e a tela associaram ordens apenas a máquinas compatíveis e ativas. A ausência de máquina foi informada e a tentativa não gravou sugestões. A regressão da CI executou a US-15 e as histórias anteriores que usam a mesma rota.

- **Bloqueio indevido da geração.** Com duas máquinas ativas e uma distribuição viável sem setup, a API devolveu 422 para uma ordem de seleção. Para os mesmos dados em ordem inversa, devolveu 201 e persistiu as duas atribuições corretas.
- **Regressão no Planejamento Manual.** Com HTTP 503 simulado exclusivamente no catálogo de máquinas, a tela ocultou ordens pendentes e planejamentos já gravados. As duas consultas que abastecem essas listas devolveram 200.
- **CT-119.** O lote misto recebe bloqueio total, como documentado no PR. A mensagem e a ausência de atribuição indevida foram comprovadas. O plano condiciona a aceitação do bloqueio total ou da geração parcial à decisão do PO, que ficou sem confirmação.
- **DoD.** A revisão do QA está registrada. Integração via PR, comprovação em homologação quando exigida e aceite do PO seguem pendentes.

## 3. Rastreabilidade

Os identificadores CT-116 a CT-119 vêm do plano anexado. As tags `US15_CT01–04` identificam cenários existentes da feature `compatibilidade.feature`. A tabela vincula cada caso pelo comportamento verificado.

| Critério ou comportamento | Caso de teste | Evidência | Resultado |
| --- | --- | --- | --- |
| C1, cada ordem associada à máquina compatível | **CT-116**. `US15_CT01` e `test_associa_maquinas_compativeis_e_persiste_sugestao`. | OP01→M01 e OP02→M02, setup zero entre máquinas, POST 201, GET igual ao POST e dois itens gravados. A tela exibe a máquina. [API e persistência](../../../backend/testes/integration/test_us15_compatibilidade.py#L83-L119) · [Cypress](../../../frontend/cypress/e2e/compatibilidade.feature#L11-L18) | **Aprovado.** |
| C1, escolha dentro do conjunto de máquinas elegíveis | **CT-117**. `US15_CT02`, teste de integração com máquina inativa e sondagem de QA com M03 ativa e incompatível. | As três ordens da sondagem foram atribuídas apenas a M01/M02 e três itens foram persistidos. O teste oficial do Cypress também cobre o critério de distribuição especificado no PR. [Filtro da API](../../../backend/app/api/routes/sugestoes_planejamento.py#L79-L91) · [Cypress](../../../frontend/cypress/e2e/compatibilidade.feature#L20-L29) | **Aprovado.** |
| C1, geração com distribuição alternativa viável | Sondagem temporária de QA, com uma ordem flexível e outra restrita a uma máquina. | A mesma seleção lógica retornou 422 ou 201 conforme a ordem dos IDs, com alocação viável no controle. [Distribuição](../../../backend/app/services/distribuicao_maquinas.py#L13-L28) · [Validação de setups](../../../backend/app/api/routes/sugestoes_planejamento.py#L93-L139) | **Reprovado** no cenário adicional. |
| C2, produto sem máquina compatível | **CT-118**. Sondagem de ordem única e `US15_CT03`, que usa uma seleção mista. | Ordem única com outra máquina ativa cadastrada e sem vínculo recebeu HTTP 422 com código da ordem e produto, zero sugestões e zero itens. No Cypress a mensagem foi exibida. [API](../../../backend/app/api/routes/sugestoes_planejamento.py#L85-L91) · [Cypress](../../../frontend/cypress/e2e/compatibilidade.feature#L31-L37) | **Aprovado.** |
| C2, limite com somente máquina inativa | `US15_CT04` e variante parametrizada de `test_bloqueia_ordem_sem_maquina_compativel_ativa`. | HTTP 422, mensagem identifica ordem sem máquina compatível ativa e não há gravação. [Integração](../../../backend/testes/integration/test_us15_compatibilidade.py#L159-L194) · [Cypress](../../../frontend/cypress/e2e/compatibilidade.feature#L39-L45) | **Aprovado.** |
| Integração US-13/US-15 com ordens compatíveis e uma incompatível | **CT-119**. `US15_CT03` e teste de integração no caso sem máquinas. | Seleção com OP01 elegível e OP02 sem vínculo devolve 422 no lote, identifica OP02 e grava zero itens ou cabeçalhos. [Integração](../../../backend/testes/integration/test_us15_compatibilidade.py#L159-L194) · [Cypress](../../../frontend/cypress/e2e/compatibilidade.feature#L31-L37) | **Executado.** Mensagem e ausência de alocação indevida confirmadas. Política de lote pendente de confirmação pelo PO. |
| Proteção da API e regressão de acesso | Teste de integração da US-13 e Cypress CT-85. | POST exige sessão e perfil, retornando 401 sem sessão e 403 para Operador. As duas rotas de consulta também retornam 403 para Operador. O CT-85 exercita a recusa pela API e verifica os registros. [Teste de permissões](../../../backend/testes/integration/test_us13_sequencia_sugerida.py) · [Log da CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928602) | **Aprovado.** |
| Integração com setup e urgência por máquina | Testes US-13 e US-14, incluindo `test_prazo_e_prioridade_por_maquina_com_inicio_independente` e `test_urgencia_incompleta_em_outra_maquina_impede_persistencia`. | Sequenciamento independente por máquina, setup direcional onde aplicável, primeira operação com setup zero, regras da US-14 preservadas e rejeição sem gravação em caso de dados de urgência incompletos. [Integração US-14](../../../backend/testes/integration/test_us14_prazos_prioridades.py#L200) · [Serviço](../../../backend/app/services/sequenciamento_maquinas.py#L26-L53) | **Aprovado na regressão executada.** |

## 4. Testes executados e resultados

| Natureza | Comando ou procedimento | Resultado e evidência |
| --- | --- | --- |
| Revisão estática | `git diff --check origin/main...HEAD` e inspeção de rota, validações, consultas, modelo, migrations, frontend e workflow. | Diff sem erros de whitespace. A lista de máquinas considera compatibilidade e atividade. A sugestão grava a escolha e a chave estrangeira referencia a máquina. [Implementação](../../../backend/app/api/routes/sugestoes_planejamento.py#L65-L139) · [Modelo](../../../backend/app/models/sugestao_planejamento.py#L45-L66) |
| Lógica isolada | `python -m pytest -q testes/unit/test_us15_sequenciamento.py` em Python 3.12.14. | **9/9** locais em 0,05 s. Também executados em Python 3.11 nas suítes completas. |
| Integração em processo com banco real | Localmente, `python -m pytest -q --junitxml=<caminho>/pytest.xml testes`. Na CI, `python -m pytest -v --junitxml=junit.xml testes`. FastAPI/TestClient e PostgreSQL 18. | **246/246 localmente em 126,82 s** e **246/246 na CI**. Inclui 9 unitários e 6 integrações da US-15 e 11 integrações da US-14. [Log do job](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928713) · [JUnit publicado](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/artifacts/15057215040) |
| Sondagens temporárias de QA com API e banco reais | `python -m pytest -s -q <caminho>/test_sondagem_us15.py`. Usa TestClient, PostgreSQL 18.6 e a instância descartável de QA. | **4 sondagens concluídas em 5,54 s**. CT-117, CT-118, reprodução do bloqueio e leitura de compatibilidade durante edição concorrente. O teste de reprodução confirma o defeito. |
| Ensaio temporário de migração com banco real | `python -m pytest -q <caminho>/test_migracao_us15.py`. Upgrade até a US-14, preparação de uma sugestão legada, upgrade até `b872837156bd` e consulta GET. | **1/1 em 4,75 s**. HTTP 200 preservou as duas ordens, posições e setups 5/30 min, com `maquina_id` nulo nos itens legados. [Coluna e FK](../../../backend/migrations/versions/7c15a3e9d204_adiciona_maquina_sugestao_us15.py#L13-L31) · [União das revisões](../../../backend/migrations/versions/b872837156bd_unifica_migrations_us14_e_us15.py#L14-L23) |
| E2E local com serviços reais | `npm run test:e2e -- --browser chrome --tags "@US15 and not @wip"` após o upgrade no banco E2E e `npm run build`. | **4/4** no Chrome, em 55,96 s. Frontend, API e PostgreSQL reais. O resumo registra `ca23d0f` e `dirty: false`. |
| E2E na CI com serviços reais | `alembic upgrade head`, API Uvicorn, frontend compilado, PostgreSQL e `npm run test:e2e:regressao -- --browser <chrome ou electron>`. `cy.intercept` observa a resposta real da sugestão. | **59/59** no Chrome e **59/59** no Electron, com **4/4 da US-15 em cada navegador**. [Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928602) · [Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928800) |
| Cypress com respostas simuladas | Job separado de login com `cypress.config.ts`. | **12/12** no Chrome, no escopo de autenticação desse job. [Log de login](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928984) |
| Sondagem de interface com falha simulada | Cypress local, spec temporária `ui-sondagem.cy.js` e configuração `cypress-sondagem.cjs`, com frontend, API e banco reais. Apenas a resposta de `GET /api/maquinas` foi substituída por 503. | **1 sondagem concluiu e reproduziu a regressão** em 3,69 s. A tentativa inicial parou antes da simulação porque o menu estava recolhido na viewport padrão. A repetição usou a viewport desktop do projeto. |
| Verificação de frontend na CI | `npm run lint` e `npm run build`. | Ambos aprovados. [Log de lint e build](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/job/139456928427) |

O nome do job de aceite menciona US11, US13 e US32. O filtro `@regressao and not @wip` inclui a feature da US-15 e os logs registram seus quatro casos nos dois browsers. As evidências locais do autor registram `commit: 39ab129` e `dirty: true` no resumo Cypress. Os logs e artefatos da CI vinculam a execução ao head do PR e ao checkout do merge de teste. [Workflow](../../../.github/workflows/ci.yml#L84-L145) · [Resumo do autor](../../releases/release2/sprint3/evidencias/us15/chrome-regressao-resumo.json) · [Artefatos Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/artifacts/15056456864) · [Artefatos Electron](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438/artifacts/15057095822)

Os XMLs do backend e da migração, as sondagens temporárias, o resumo local do Chrome e suas capturas estão em `.tmp/qa-us15/` no workspace de QA. Os comandos e dados descritos permitem repetir os cenários em banco descartável.

Para reproduzir, use o commit avaliado, dependências de `requirements.txt` e PostgreSQL de teste dedicado com `TEST_DATABASE_URL` terminando em banco `_test`. Execute no diretório `backend`.

```powershell
python -m pytest -q --junitxml=pytest-us15.xml testes
python -m pytest -v testes/unit/test_us15_sequenciamento.py testes/integration/test_us15_compatibilidade.py testes/integration/test_us13_sequencia_sugerida.py testes/integration/test_us14_prazos_prioridades.py
```

Para Cypress, prepare outro banco com sufixo `_e2e_test`, aplique as migrations, inicie API e frontend e configure `E2E_DATABASE_URL` conforme o guia. Execute a partir de `frontend`. [Guia do Cypress](../../../frontend/cypress/README.md#ambiente-local)

```powershell
npm run test:e2e -- --browser chrome --tags "@US15 and not @wip"
npm run test:e2e -- --browser chrome --tags "(@US13 or @US14 or @US15) and not @wip"
npm run test:e2e:regressao -- --browser electron
```

## 5. Bugs e pendências

### A geração rejeita ordens que podem ser separadas em máquinas compatíveis

- **Classificação e severidade sugerida.** Bug funcional confirmado, **média**. Bloqueia a geração de uma sugestão viável para o Planejador. Alterar somente a ordem de seleção contorna o bloqueio no cenário reproduzido.
- **Comportamento afetado.** C1, geração com máquinas compatíveis. A distribuição escolhe primeiro com base nas contagens e no código da máquina. A verificação de setup ocorre depois, apenas para as famílias que a distribuição colocou na mesma máquina. [Distribuição](../../../backend/app/services/distribuicao_maquinas.py#L13-L28) · [Validação e retorno](../../../backend/app/api/routes/sugestoes_planejamento.py#L93-L139)
- **Pré-condições e passos.** Cadastre M01 e M02 ativas. Crie OP01 da família A compatível com M01/M02 e OP02 da família B compatível somente com M01. Mantenha A→B e B→A sem configuração e use ordens pendentes sem dados de urgência. Faça POST para `/api/planejamentos/sugestoes` com os IDs em `[OP01, OP02]`. Repita com `[OP02, OP01]` sem mudar o cadastro.
- **Esperado.** Gerar uma sugestão viável com OP01→M02, OP02→M01 e setup total 0 nas duas seleções. Essa distribuição usa as compatibilidades cadastradas e dispensa trocas de família na mesma máquina.
- **Obtido.** A primeira seleção devolveu **422**, informando setup A→B e B→A sem cadastro, com zero sugestões e itens. A segunda devolveu **201** com as duas máquinas esperadas, setup zero e dois itens persistidos.
- **Evidência e limite.** Reprodução pela API com TestClient e PostgreSQL local, em dados fictícios. A outra seleção foi o controle positivo. O cenário foi executado no backend. As mensagens e a persistência foram verificadas.

```gherkin
Cenário: Gerar uma sugestão quando as máquinas podem separar as famílias
  Dado que a OP01 da família A é compatível com M01 e M02 ativas
  E que a OP02 da família B é compatível somente com M01
  E que não há tempos de setup cadastrados entre A e B
  Quando o Planejador solicitar a sugestão selecionando OP01 antes de OP02
  Então a sugestão deve atribuir OP01 à M02 e OP02 à M01
  E deve gravar uma sugestão com duas ordens e setup total de zero minuto
```

### Falha no catálogo de máquinas esvazia as listas de Planejamento Manual

- **Classificação e severidade sugerida.** Bug de regressão confirmado em teste controlado, **média**. Impede consultar planos salvos e selecionar ordens pendentes enquanto só o catálogo está indisponível. A API continuou devolvendo os dados salvos.
- **Comportamento afetado.** US-12 e entrada para geração/consulta da sugestão. A US-15 incluiu o catálogo no carregamento conjunto. Um 503 faz a tela lançar o erro antes de preencher as listas de ordens e planejamentos. [Carregamento da página](../../../frontend/src/features/planejamentos/pages/PlanejamentosPage.tsx#L62-L94)
- **Pré-condições e passos.** Use uma sessão de Planejador, um plano salvo para OP01 e uma ordem OP02 pendente. Confirme que ambos aparecem no Planejamento Manual. Com Cypress, intercepte só `GET /api/maquinas` com HTTP 503. Recarregue, abra a página e inspecione também os GETs de ordens e planejamentos.
- **Esperado.** O plano e as ordens devolvidos com 200 continuam visíveis. O erro informa a indisponibilidade do catálogo.
- **Obtido e evidência.** Os GETs de ordens e planejamentos devolveram 200, com o plano no corpo. A tela mostrou “Não foi possível carregar os dados.”, “Nenhuma ordem pendente disponível.” e “Nenhum planejamento cadastrado.” As capturas do controle e do 503 estão em `.tmp/qa-us15/evidencias-ui/ui-sondagem.cy.js/`, com o XML em `.tmp/qa-us15/ui-sondagem.xml`. A falha do catálogo foi simulada no navegador.

```gherkin
Cenário: Consultar o planejamento manual com o catálogo de máquinas indisponível
  Dado que há ordens pendentes e um planejamento já gravado
  E que as APIs de ordens e planejamentos retornam HTTP 200 com esses registros
  Quando o catálogo de máquinas responder HTTP 503 ao abrir Planejamento Manual
  Então a página deve manter as ordens e os planejamentos retornados visíveis
  E deve informar a indisponibilidade do catálogo de máquinas
```

### Alteração de compatibilidade concorrente pode chegar antes da gravação

- **Classificação e severidade sugerida.** Suspeita a validar, **impacto potencial médio** se a regra exigir compatibilidade vigente no momento da gravação. O resultado observado está confirmado. O critério fornecido não fixa o instante de referência durante solicitações concorrentes.
- **Pré-condições e passos.** Prepare OP01 compatível só com M01. Em uma sessão de Planejador, inicie a geração e pause o teste após a leitura das máquinas, antes de `distribuir_ordens`. Em outra sessão válida, altere o vínculo para M02, aguarde o 200 e libere a primeira geração. Gere mais uma sugestão depois.
- **Obtido.** A primeira solicitação gravou M01 com HTTP 201 após a edição para M02 já ter sido concluída. A nova solicitação gravou M02. O PostgreSQL recebeu os dois fluxos reais. A sondagem só controlou o ponto de sincronização. [Leitura e distribuição](../../../backend/app/api/routes/sugestoes_planejamento.py#L41-L93) · [Persistência](../../../backend/app/api/routes/sugestoes_planejamento.py#L196-L217)
- **Esperado e critério de encerramento.** O PO deve definir se a sugestão representa a compatibilidade lida no início ou a vigente na gravação. Dada uma edição concluída entre esses pontos, o reteste deve observar a escolha ou a recusa definida pelo contrato e preservar o histórico de sugestões já concluídas antes da edição.

### A política do lote misto aguarda confirmação

- **Classificação e severidade.** Pendência da DoD, sem severidade funcional atribuída. Afeta o **CT-119** e a evidência final dos critérios.
- **Pré-condições, ação e resultado.** Gere com uma ordem vinculada a máquina ativa e outra sem vínculo. A API devolve 422 e não grava nenhuma ordem. O Cypress confirma mensagem na tela. [Cenário automatizado](../../../frontend/cypress/e2e/compatibilidade.feature#L31-L37)
- **Esperado e encerramento.** O PO registra a política de bloqueio total ou resultado parcial. O reteste deve confirmar o resultado escolhido, identificar cada ordem sem máquina e comprovar que nenhuma delas foi atribuída nem persistida como elegível.

**Duplicidade.** A busca de issues no GitHub por US15, SC-32, compatibilidade, sequenciamento, planejamento manual e catálogo não retornou registros correspondentes. As issues de regressão [#18 da US-11](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) e [#19 do Driver06](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19) tratam de outros comportamentos e estavam fechadas. Consulte a SC-32 antes de abrir um registro separado no Jira, pois seu conteúdo não estava acessível.

## 6. Verificação da DoD

| Critério informado | Estado | Evidência ou pendência |
| --- | --- | --- |
| Código revisado e integrado via Pull Request | **Não atendido** | Revisão de QA registrada. O PR #24 ainda estava aberto e sem merge. [PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24) |
| Critérios de aceite atendidos e validados pelo QA | **Não atendido** | CT-116, CT-117 e CT-118 aprovados. Cenário adicional do C1 reprovado. A política para o CT-119 aguarda o PO. |
| Testes escritos e passando | **Atendido** | A suíte oficial, incluindo nove unitários, seis integrações e quatro cenários Cypress da US-15, passou. Os achados adicionais exigem cobertura de regressão após correção. |
| Pipeline de CI sem falhas | **Atendido** | Cinco jobs concluídos com sucesso no run do PR associado ao head avaliado. [CI #159](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45685507438) |
| Implantado em homologação, quando exigido na release | **Não verificado** | O plano de qualidade acompanha deploy em homologação para R2–R4. A exigência específica, a URL e o commit implantado ainda precisam de confirmação. [Plano de qualidade, Catálogo de métricas, B20:D20](../Plano-de-Qualidade-SetupFlow.xlsx) |
| Documentação atualizada | **Atendido** | Os guias descrevem distribuição, compatibilidade ativa, setups por máquina, consultas e migrations. A correspondência com os IDs da Sprint 3 consta neste relatório. [Backend](../../../backend/README.md#us15--compatibilidade-entre-produtos-e-máquinas-no-sequenciamento) · [Modelo de dados](../../arquitetura/modelo-de-dados.md#associação-de-máquinas-às-sugestões-na-us15) · [Cypress](../../../frontend/cypress/README.md) |
| Aceita pelo PO | **Não verificado** | Nenhuma aprovação registrada na discussão ou nas revisões consultadas do PR. A SC-32 ainda precisa ser consultada. |

## 7. Reteste e regressão

- **Reteste do bloqueio indevido.** Após ajuste, repetir as duas ordens de seleção da seção 5, verificar HTTP 201, OP01→M02 e OP02→M01, setup 0 e o mesmo par de atribuições na tela. Conferir um cabeçalho e dois itens por requisição bem-sucedida. Repetir o controle com ambas as ordens compatíveis somente com M01 e setups ausentes. Nesse caso o 422 da US-13 continua previsto.
- **Reteste do lote misto.** Registrar a decisão do PO e executar CT-119 com dados isolados. Conferir a mensagem, as ordens retornadas na API e exibidas na tela, e a quantidade de itens persistidos de acordo com a política confirmada.
- **Reteste do Planejamento Manual.** Repetir o controle saudável e a falha isolada de catálogo, com os GETs de ordens e planos mantidos em 200. Verificar a presença dos registros e a mensagem do catálogo. Restaurar o endpoint e repetir a exibição das máquinas nas sugestões.
- **Regressão executada.** O backend da CI rodou a suíte completa, incluindo US-02/03/07–10, US-12–14, US-26 e US-32. São os fluxos de perfis, estados de máquinas, cadastro de ordens, urgência, setups, planejamento manual, sugestão, compatibilidade e históricos tocados pela integração. A CI também rodou a regressão BDD com matriz de setup, sugestão US-13, prazos da US-14, compatibilidade US-15 e usuários. Login correu em job próprio.
- **Regressões históricas.** Os roteiros específicos das issues #18 e #19 com respostas simuladas ficaram fora deste reteste. A aprovação dos cenários gerais da CI não comprova essas variantes.

## 8. Limitações e ações pendentes

| Pendente | Ação |
| --- | --- |
| SC-32 e aceitação do lote misto | Confirmar com o PO a regra do CT-119, revisar a issue vigente e registrar a decisão no local usado pelo time. |
| Bloqueio da sugestão viável | Corrigir a distribuição ou o tratamento de alternativas e incluir o cenário da seção 5 na automação. |
| Catálogo de máquinas indisponível | Retestar a página com as respostas específicas da seção 5. A disponibilidade real em homologação ficou sem medição nesta revisão. |
| Concorrência | Definir o instante de referência para a compatibilidade. Repetir a sondagem com duas sessões no ponto definido, após ajuste se aplicável. |
| Homologação e integração | Identificar ambiente e commit implantado, quando exigido. Repetir geração válida, incompatibilidade, acesso do Operador e recuperação da sugestão. Conferir a CI da revisão candidata e o aceite do PO. |

## 9. Parecer final

**Pendente de ajustes.** A API e a interface passaram nos fluxos nominais, inclusive o bloqueio de atribuição incompatível. A API rejeitou uma sugestão viável conforme a ordem de seleção e a tela ocultou dados do Planejamento Manual quando o catálogo falhou. A política do lote misto precisa de confirmação e a integração via PR está pendente. O parecer de QA não substitui o aceite do PO.

### Comentário para a issue ou o PR

> QA revisou o commit `ca23d0f4e775719c40926f1de12d3b7d6b096a93`. Passaram 246 testes de backend e 59 cenários por navegador na CI, com os quatro casos da US-15 em Chrome e Electron. Reproduzi um 422 apesar de existir uma distribuição compatível sem setup e uma regressão que oculta ordens e planos quando o catálogo de máquinas responde 503. O CT-119 aguarda confirmação do PO sobre o lote misto, e a integração do PR está pendente. **Parecer de QA — Pendente de ajustes.** [Inserir link do relatório]
