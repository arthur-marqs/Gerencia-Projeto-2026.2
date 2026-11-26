# Relatório de Qualidade — Release 2

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Projeto | SetupFlow, Release 2, Sprints 2 e 3 |
| QA responsável pela release | Leonardo Istamilo, conforme os papéis registrados no projeto |
| Preparação, execução e registro deste ciclo | Codex. A conferência humana do fechamento da release continua pendente. |
| Período das evidências históricas consultadas | 05 a 26/11/2026. As datas indicam as evidências encontradas, e o calendário completo da sprint ficou indisponível. |
| Ciclo | R2-REG-20261126-08a62f5, 26/11/2026, America/Sao_Paulo (UTC−03:00) |
| Repositório e versão candidata | `arthur-marqs/Gerencia-Projeto-2026.2`, remoto `origin`, `main` em [`08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`][main] |
| Checkout e alterações locais | Cópia isolada em HEAD destacado. O código e as suítes oficiais vieram do commit identificado. Os ensaios auxiliares constam do registro do ciclo. A árvore original estava limpa na branch `docs/qualidade` antes do trabalho. |
| Versão complementar | [`ee2a4a88aea0018cb451c8f9988346fe25551e7a`][corrigida], `docs/qualidade`, com as duas correções, executada em outra cópia isolada |
| Tag | `v0.1.0` identifica a Release 1 e é a única tag do remoto. A Release 2 está sem tag identificada. [Consulta do remoto][github] |
| Ambiente de execução | Windows x64, build 26300, Python 3.11.9, PostgreSQL 18.6, Node.js 26.13.0 e Cypress 16.3.0. API, frontend e bancos locais descartáveis. [Ambiente e comandos][regressao] |

## 2. Resumo executivo

**Estado após o merge.** Em 26/11/2026, o PR #32 integrou as correções dos BUG-004 e BUG-005 à `main` em `c43587c`. O código e as suítes do produto nesse merge correspondem aos do commit `ee2a4a8`, no qual os dois retestes passaram. A regressão documentada abaixo mantém os seus SHAs de execução. A CI do merge estava em execução na consulta. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) · [CI do merge](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45882475010)

**Parecer de QA · Pendente de ajustes para `08a62f5`.** A regressão da versão integrada exercitou as entregas da Release 2 e voltou a encontrar o defeito de aprovação com máquina inelegível. As duas variantes deixaram a sugestão disponível, retornaram HTTP 201 e publicaram um plano que o Operador conseguiu consultar. No fluxo nominal completo, a preparação, o plano manual, a sugestão, a comparação, a aprovação e a consulta passaram na mesma execução. [Registro do ciclo][regressao] · [Evidência do BUG-004][main-bug004]

As issues #18, #19, #25, #30 e #31 estão fechadas. No ciclo anterior ao merge, a regressão em `08a62f5` registrou 325 testes oficiais de backend aprovados, 67 cenários por navegador e 12 de autenticação no Chrome. Os ensaios adicionais reproduziram os BUG-004 e BUG-005 nesse SHA. Os retestes específicos passaram em `ee2a4a8`. [Resultados][regressao]

## 3. Escopo da release

O [registro de entregas](../../status-projeto.md#release-2), os PRs e os relatórios de revisão sustentam o recorte de 11 histórias e quatro drivers. A atribuição à Sprint 2 usa o relatório da US32 e os PRs do incremento de cadastros e planejamento manual. A Sprint 3 usa as revisões que citam essa sprint e a matriz CT-105 a CT-137 reproduzida na auditoria. A íntegra do plano da Release 2 e sua programação no Jira ficaram indisponíveis ao ciclo.

| Sprint | Histórias | Drivers |
| --- | --- | --- |
| 2 | [US09](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/10) duração estimada, [US10](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/11) setup direcional, [US12](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/12) planejamento manual, [US26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/9) compatibilidade produto–máquina, [US32](sprint2/relatorio-alinhamento-us32.md) gestão de usuários | [Driver02](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/13), idempotência no cadastro de ordens |
| 3 | [US11](sprint3/relatorio-revisao-pr16-us11.md) matriz de setup, [US13](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/22) sugestão, [US14](../../qualidade/release-2/revisao-us14.md) prazos e prioridades, [US15](../../qualidade/release-2/revisao-us15.md) máquinas elegíveis, [US16](../../qualidade/release-2/revisao-us16.md) comparação, [US17](../../qualidade/release-2/revisao-us17.md) aprovação e consulta | [Driver01](../../qualidade/release-2/revisao-driver01.md) integridade, [Driver04](../../qualidade/release-2/revisao-driver04.md) autorização, [Driver06](../../qualidade/release-2/revisao-driver06.md) sessões expiradas ou invalidadas |

As US01 a US08 e o Driver05 são regressão da Release 1. A execução do Operador no incremento consiste em consultar o plano aprovado. Registro de início e conclusão, replanejamento e indicadores fazem parte da evolução documentada. A cobertura vinculada a esses fluxos está indicada na seção 6.

## 4. Estratégia e cobertura

- **Backend.** Pytest completo, incluindo testes unitários e integração pelo TestClient com PostgreSQL real. A cobertura abrange login, logout, permissões, usuários, cadastros, ordens, prazos, prioridades, duração, tempos direcionais e planejamento. [Resultados por classe e caso][backend]
- **Aceite no navegador.** Cypress/Gherkin das histórias de planejamento, matriz e usuários, com API e banco reais. Cenários da matriz, catálogo e autenticação simulam as respostas específicas indicadas no roteiro. A validação real de sessão e autorização baseia-se nos ensaios da API e do navegador registrados na seção 6. [Cenários e execução][regressao]
- **Fluxo RG-01.** Em um teste de API com persistência real, foi criada a massa A/B/A, cadastrados setups assimétricos, salvos o manual e a sugestão e comparados 50 e 20 minutos, respectivamente. A sugestão aprovada persistiu três itens e o Operador recebeu a mesma sequência. O cenário usa as regras já verificadas nas US13, US16 e US17. [Teste e evidência][main-bug004]
- **Retestes.** Cenários oficiais de BUG-001, BUG-002 e BUG-003, sondagens do BUG-004 e do BUG-005 sob as duas versões, medição HTTP dos drivers e verificação complementar de lint e build. A cobertura e o método de cada caso estão no [registro de regressão][regressao].
- **Exclusões.** Ensaio de carga p95 das operações principais, homologação, execução humana integral do plano e validação de funcionalidades futuras dependem de fontes, ambiente ou incremento separado. A política do lote misto do CT-119 e a aplicabilidade da homologação permanecem para confirmação. Os resultados no ambiente local ou os aceites já comunicados permanecem evidência do escopo identificado.

## 5. Ciclo de regressão

| Versão | Execução | Resultado |
| --- | --- | --- |
| `08a62f5` | Pytest oficial completo | **325 aprovados**, 0 falhas, erros ou ignorados, 199,08 s de ferramenta, saída 0. [Evidência][backend] |
| `08a62f5` | RG-01 e BUG-004 na API | **1 aprovado e 2 reprovados**. As duas reprovações são variantes do mesmo defeito. [Evidência][main-bug004] |
| `08a62f5` | Cypress regressão Chrome e Electron | **67/67 por navegador**, 0 falhas, pendências ou ignorados. 443,90 s e 389,26 s de ferramenta, respectivamente. |
| `08a62f5` | Cypress autenticação e ensaio BUG-005 | **12/12** oficiais. No ensaio integrado, **1 aprovado e 2 reprovados**, saída 2. |
| `08a62f5` | Drivers, lint, build e migrações | Medições na seção 6. Lint, build e migrações concluíram com saída 0. |
| `ee2a4a8` | Retestes e regressões complementares | **3/3** em RG-01 e BUG-004, **13/13** na suíte US17, **17/17** em autenticação e **3/3** no reteste integrado de sessão. Saída 0 em cada execução. |

O [registro detalhado][regressao] traz horários, saída e duração por comando, as amostras de medição, os casos do plano que puderam ser rastreados e os impedimentos. Os totais de ferramentas são contagens por execução.

## 6. Validação dos drivers

| Driver | Meta recuperada das fontes | Método e amostra | Resultado medido na `main` | Evidência | Situação |
| --- | --- | --- | --- | --- | --- |
| Driver01 | Reagir corretamente a 100% de ≥20 interrupções, ao menos 10 cadastros e 10 atualizações, preservando os dados confirmados, sem gravação parcial e com indicação da falha | HTTP real em Uvicorn. Encerramento controlado da conexão da transação de teste após escrita e antes do commit. Conferência por outra conexão, com reenvio e controles positivos | 20/20 HTTP 503, 0 gravações parciais, 3/3 controles válidos e 20/20 recuperações | [Amostras][driver01] · [Revisão](../../qualidade/release-2/revisao-driver01.md) | **Atendida para as gravações de ordens disponíveis.** Andamento da execução indisponível para CT-127/128/129 na variante correspondente. |
| Driver02 | 20 operações com resposta perdida após commit e cinco reenvios por operação, mantendo os IDs e sem duplicar ordens. Verificar janela de 24 h, nova chave e concorrência | Pytest com commit real e perda de resposta induzida. Oito testes do driver, incluindo a amostra de 20 cadastros e 100 reenvios. A fronteira usa relógio controlado | Oito testes aprovados. O teste quantitativo exige 20 registros únicos, um por chave, e todos os IDs devolvidos iguais aos IDs persistidos | [Pytest][backend] · [Suíte oficial](../../../backend/testes/integration/drivers/test_driver02_idempotency_ordens.py) | **Atendida no cenário testado.** O ensaio de 24 h simula a passagem do tempo. |
| Driver04 | Bloquear 100% de ≥20 acessos distintos, ao menos 10 de cada condição, sem exposição de dados ou alteração do banco e com controles de Planejador | TestClient + PostgreSQL com dados válidos, incluindo candidatos e aprovação. Comparação de estado antes e depois | 14/14 com Operador (403), 14/14 sem sessão (401), 28/28 sem alteração nem dados protegidos na resposta e 14/14 controles positivos. A suíte oficial passou separadamente em 44 casos. | [Matriz][driver04] · [Revisão](../../qualidade/release-2/revisao-driver04.md) | **Atendida nas rotas disponíveis.** Replanejamento ficou fora da matriz. |
| Driver06 | Rejeitar 100% de ≥20 acessos expirados/invalidados com cada resposta ≤2 s e solicitar nova autenticação. A revisão exige controles de sessão válida e perfil autorizado | Uvicorn/PostgreSQL com expiração gravada no banco e invalidação real por logout. 20 GETs por estado, alternados em oito rotas, e uma escrita adicional por estado. Chrome no fluxo de Famílias | 60/60 GETs devolveram 401, dos quais 20 expirados, 20 invalidados e 20 com token desconhecido como controle. Três escritas retornaram 401 sem gravar. Máximos HTTP de **30,743 ms**, **14,366 ms** e **26,793 ms**, respectivamente. No Chrome, 20/20 recusas, com máximo de **17,3 ms** até a resposta e **19,4 ms** até o formulário. | [HTTP][driver06] · [Revisão](../../qualidade/release-2/revisao-driver06.md) | **Atendida no loopback para os dois marcos medidos.** Aplicabilidade em homologação e interpretação formal do marco continuam a confirmar. |

O tempo do Driver06 é avaliado pelo máximo individual de cada condição. O prazo de 2 s tem evidência de resposta HTTP no loopback, e a interpretação formal do marco final continua com o PO. As medições dessa recusa não representam o p95 das operações principais de Q-07. O Driver05 permaneceu no ciclo como regressão da Release 1, incluindo os 20 ciclos e 200 tentativas adicionais bloqueadas previstos no seu teste. [Pytest][backend] · [Plano de riscos](../../qualidade/GP-RiscoBaseadoDefeitos-SetupFlow.xlsx)

## 7. Bugs encontrados e corrigidos

| Registro | Severidade registrada | Fix e integração à `main` | Reteste | Estado da issue |
| --- | --- | --- | --- | --- |
| [BUG-001, #18][issue18], famílias ausentes nos eixos da matriz | Média | `47c63d6` e `bbf29c4`, [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16), merge `8d654d3`. O PR #21 complementou o registro e as evidências | As variantes de origem e destino ausentes passaram no Chrome. [Comentário de QA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18#issuecomment-7109530230) | Fechada |
| [BUG-002, #19][issue19], interface após 401 com identidade indisponível | Média | `67fa646`, [PR #17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/17), merge `a118dcd` | Famílias e Máquinas passaram após HTTP 401 no Chrome. [Comentário de QA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19#issuecomment-7112231551) | Fechada |
| [BUG-003, #25][issue25], distribuição viável rejeitada | Média | `ae8ae27`, [PR #24](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24), merge `db73ab8` | Duas ordens de seleção aprovadas no Pytest. O cenário de redistribuição também passou no Chrome. O outro comentário da issue descreve a US11 e foi excluído desta rastreabilidade. [Comentário correto](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/25#issuecomment-7176630592) | Fechada |
| [BUG-004, #30][issue30], aprovação após mudança de elegibilidade | Alta | [`b6c72f2`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/b6c72f2), validada em `ee2a4a8` e integrada em `c43587c` pelo [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) | As duas variantes reprovaram em `08a62f5` com 201 e persistência. Na branch corrigida, 2/2 retornaram 409, sem publicação, e a suíte US17 passou em 13/13. [Reteste anterior](../../qualidade/release-2/auditoria-bugs/reteste-bug004.md) · [Novo ciclo][regressao] | Fechada |
| [BUG-005, #31][issue31], falha temporária na restauração da sessão | Média | [`8978fc1`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/8978fc1), validada em `ee2a4a8` e integrada em `c43587c` pelo [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) | Em `08a62f5`, dois casos reprovaram pela ausência do aviso e da ação de nova tentativa depois do 503. Na branch corrigida, 3/3 retestes integrados e 17/17 cenários oficiais de autenticação passaram. [Reteste anterior](../../qualidade/release-2/auditoria-bugs/reteste-bug005.md) | Fechada |

**Correções internas de PR.** A falha do catálogo que ocultava o plano e impedia abrir a comparação foi corrigida na US16 por `1e98b76`, integrada no PR #27. A referência de usuários aprovadores passou a bloquear exclusão física em `c06fb94`, no PR #28, e o teste de regressão de usuários consta do Pytest. A concorrência da idempotência e a tipagem de UUID foram ajustadas em `c172886`, incluído no PR #17, e a suíte do Driver02 foi exercitada. O tratamento da recusa de sessão na geração de sugestões entrou em `0551a78`, PR #22. Esses registros internos têm rastreio no Git, sem triagem de severidade no conjunto consultado. [Revisão US16](../../qualidade/release-2/revisao-us16.md) · [Pytest][backend] · [Histórico da main][main]

O ciclo reproduziu os dois defeitos conhecidos. Nos cenários adicionais exercitados, nenhum novo defeito de produto foi identificado. A reavaliação das correções se aplica à cópia `ee2a4a8`.

## 8. Verificação da DoD

A matriz segue os sete critérios do [DoD vigente](../../status-projeto.md#definition-of-done-dod). Usa **Atendido**, **Não atendido**, **Não verificado** e **Não se aplica**. O aceite do PO foi comunicado para os itens integrados e registrado em `2a7ad66`. A coluna PO usa essa confirmação. A ata ou o ticket individual da Release 2 ficaram indisponíveis. O parecer técnico desta regressão se aplica ao SHA indicado.

| Item e merge | Revisão e integração via PR | Critérios validados pelo QA | Testes passando | CI | Homologação se exigida | Docs | PO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US09 · #10 `08627f2` | Atendido | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US10 · #11 `7f93ea6` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US11 · #16/#21 `8d654d3`/`8f992a1` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US12 · #12 `49e19c9` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US13 · #22 `e5d73f1` | Atendido | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US14 · #23 `39ab129` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US15 · #24 `db73ab8` | Não verificado | Não verificado | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US16 · #27 `10cdd8a` | Atendido | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US17 · #28 `5772ec0` | Atendido | Não atendido | Não atendido | Atendido | Não verificado | Atendido | Atendido |
| US26 · #9 `a3b6fb2` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| US32 · #15 `5cf655e` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| Driver01 · #26 `65a1d24` | Não verificado | Não verificado | Atendido | Atendido | Não verificado | Atendido | Atendido |
| Driver02 · #13 `aae2669` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| Driver04 · #29 `08a62f5` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |
| Driver06 · #17 `a118dcd` | Não verificado | Atendido | Atendido | Atendido | Não verificado | Atendido | Atendido |

- **Revisão e integração.** Todos os merges citados são ancestrais da `main`. Quatro dos 16 PRs de entrega consultados têm revisão formal publicada antes do merge. Nos demais, a evidência prova a integração e a revisão formal via PR ficou sem confirmação. [Consulta de integração e revisões][github]
- **QA e testes.** O [mapa do ciclo][regressao] liga os casos, perfis e suítes a cada US e driver. Na US15, CT-119 exercitou a política observada, com a regra oficial do lote misto a confirmar. Para o Driver01, a conclusão integral do estímulo depende da operação de andamento. Na US17, duas variantes do BUG-004 reprovaram apesar da suíte oficial verde.
- **CI.** Cinco jobs do [GitHub Actions][ci] concluíram com sucesso no commit integrado. O registro de execução local cobre cenários adicionais, inclusive as reprovações do BUG-004.
- **Homologação.** A obrigatoriedade e o SHA implantado ficaram **Não verificados** para os 15 itens. O ciclo usou ambiente local. A equipe pode aplicar **Não se aplica** somente após confirmar que a release dispensa homologação.
- **Documentação e aceite.** [Registro das entregas](../../status-projeto.md), [documentação da release](README.md), [guias backend](../../../backend/README.md) e [Cypress](../../../frontend/cypress/README.md). O aceite informado se refere às entregas identificadas. A liberação da versão integrada permanece uma decisão da equipe após os ajustes.

## 9. Métricas de qualidade

**Execução (%)** = (aprovados + reprovados) ÷ casos planejados × 100. **Aprovação (%)** = aprovados ÷ (aprovados + reprovados) × 100. Denominador zero resulta em **Não se aplica**. Denominador ou conjunto incompleto é **Não levantado**. Casos do plano, exemplos parametrizados, tentativas de uma medida e repetições em outros navegadores têm unidades próprias.

### A. Histórico das Sprints 2 e 3

| Recorte histórico | Resultado verificável | Limite |
| --- | --- | --- |
| Sprint 2, US32 | 197 Pytest aprovados, 42 da US32 dentro desse total. 32 cenários aprovados por navegador em Chrome e Electron para o conjunto de 12 critérios. O smoke repetiu cinco cenários. [Relatório](sprint2/relatorio-alinhamento-us32.md) | O total de casos planejados e a distribuição de resultados de toda a Sprint 2 ficaram **Não levantados**. |
| Sprint 3, revisões das histórias e dos drivers | Relatórios da US11, US14, US15, US16, US17, Driver01/04/06 e retestes registram datas, commits e escopos diferentes. Em 26/11, a auditoria de `08a62f5` registrou 325 Pytest, 67 Cypress de regressão e 12 de autenticação aprovados, além de dois defeitos exploratórios. [Auditoria anterior](../../qualidade/release-2/auditoria-bugs/relatorio-validacao.md) | A série do mesmo teste entre branches, fases e navegadores permanece separada. Planejados, executados, aprovados, reprovados, bloqueados, não executados e ignorados do plano completo da sprint ficaram **Não levantados**. |

### B. Resultado do ciclo final de regressão

| Conjunto na main | Planejados | Executados | Aprovados | Reprovados | Bloqueados | Não executados | Ignorados | Execução | Aprovação |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Recorte de IDs do plano rastreados | 48 | 41 | 41 | 0 | 7 | 0 adicionais | Não se aplica | 85,42% | 100% |
| Pytest oficial, casos coletados pela ferramenta | 325 | 325 | 325 | 0 | 0 | 0 | 0 | 100% | 100% |
| Regressão Cypress, por navegador | 67 | 67 | 67 | 0 | 0 | 0 | 0 | 100% | 100% |
| Autenticação oficial Cypress | 12 | 12 | 12 | 0 | 0 | 0 | 0 | 100% | 100% |
| RG-01 e BUG-004, ensaios de API | 3 | 3 | 1 | 2 | 0 | 0 | 0 | 100% | 33,33% |
| BUG-005 e controle Driver06, ensaio de navegador | 3 | 3 | 1 | 2 | 0 | 0 | 0 | 100% | 33,33% |

Os sete bloqueados compreendem CT-119, CT-127–129 e CT-135–137. Eles incluem verificações parciais e ficaram fora do numerador de execução por ID. Os 100% de aprovação do recorte se referem aos 41 IDs concluídos. As quatro reprovações dos ensaios complementares continuam válidas para o parecer da versão. Para o **plano completo**, os totais e percentuais ficaram **Não levantados**. [Casos e contagens][regressao]

O fluxo RG-01 e as variantes dos bugs são ensaios complementares. As medições de 20, 28 e 60 tentativas pertencem aos drivers e não foram somadas como casos únicos do plano.

### C. Situação atual da release

Cinco bugs com issue pública identificada. Distribuição **1 alta, 4 médias**. As cinco correções estão na `main`, e as cinco issues estão fechadas na consulta pós-merge. Os BUG-004 e BUG-005 passaram no reteste em `ee2a4a8`. O total no Jira e a distribuição dos registros internos sem severidade ficaram **Não levantados**. [Integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32)

| Métrica do plano de qualidade | Meta versionada | Situação para a Release 2 |
| --- | --- | --- |
| Q-01 Execução | 100% dos casos das US entregues | **Não levantado** no plano completo. O ciclo usa o recorte rastreável descrito no registro. |
| Q-02 Aprovação | ≥95% no fim da release | **Não levantado** no plano completo. Percentuais de ferramenta e do recorte estão na seção B. |
| Q-03 Bugs altos ou críticos em aberto | 0 no fechamento da release | No ciclo de `08a62f5`, o BUG-004 alto estava aberto. Após o merge, as cinco issues públicas verificadas estão fechadas. Contador Jira **Não levantado**. |
| Q-04 Critérios definidos antes da sprint | 100% das histórias | **Não verificado**. DoR e histórico do Jira indisponíveis. |
| Q-05 Revisão antes do merge | 100% dos PRs | **25,00% com revisão formal identificada** (4/16 PRs de entrega R2). O PR de cobertura #14 não integra o denominador de entregas por US/driver. |
| Q-06 Pipeline principal | Aprovado | **Atendido para `08a62f5`**, cinco jobs verdes. O [pipeline do SHA de merge](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45882475010) estava em execução na consulta. |
| Q-07 Tempo de resposta das operações principais | p95 ≤2 s | **Não medido**. O Driver06 usa limite por recusa e escopo próprios. |
| Q-08 Autorização por perfis | 100% dos perfis | A API exercitou permissões de Planejador, Operador e Administrador. A matriz de negativas e controles positivos consta no Driver04, e as suítes US02/US32 cobrem os perfis disponíveis. [Pytest][backend] |
| Q-09 Tratamento dos fluxos principais | 100% | **Não atendido no recorte**, pois há cenários de exceção com falha observada. A taxa global ficou **Não levantada**. |

O [plano de qualidade](../../qualidade/Plano-de-Qualidade-SetupFlow.xlsx) é a versão 1.1 de 29/10/2026 disponível no repositório. A coluna R2 estava em branco. As metas usadas são da aba **Plano de qualidade**, itens Q-01 a Q-09. Exemplos do catálogo não foram promovidos a metas da release.

## 10. Riscos e limitações

| Risco ou lacuna | Evidência e consequência | Responsável e ação sugerida |
| --- | --- | --- |
| Máquina inelegível em sequência aprovada | BUG-004 reproduzido no SHA candidato. Pode disponibilizar uma sequência impraticável ao Operador. | Correção integrada. QA e DevOps acompanham a CI e os retestes no SHA de fechamento. |
| Restauração de sessão válida após falha temporária | BUG-005 reproduzido em `08a62f5`. A correção entrou em `c43587c`. | QA acompanha os retestes de 503 de identidade, recusa 401 e resposta atrasada no SHA de fechamento. |
| Falhas intermitentes de ambiente | Histórico de memória do Argon2, incluindo CT-85 e CT-35, e timeout do Chrome em execução anterior. As reexecuções sequenciais históricas passaram. Os logs deste ciclo não registraram nova falha de memória do Argon2 nem timeout operacional do navegador. O timeout de asserção do BUG-005 correspondeu à ausência do aviso esperado. | QA e DevOps, manter execução sequencial e preservar logs da primeira falha antes de repetir. |
| Regra do CT-119, escopo de andamento e marco de 2 s | Lote misto é bloqueado no produto. O plano citado pede confirmação do PO. Andamento e replanejamento não estão disponíveis neste incremento. | PO e QA, recuperar o plano vigente e registrar a política do lote, o alcance das variantes e o marco da medida. |
| Reversão da migração da US14 | A revisão histórica reproduziu falha de downgrade após sugestão com aumento de setup. A migração de subida faz parte deste ciclo. | DevOps, validar a reversão em banco descartável com dados representativos. [Revisão](../../qualidade/release-2/revisao-us14.md#downgrade-falha-após-gravar-sugestão-válida-com-aumento-de-setup) |
| Homologação, desempenho e rastreabilidade | Candidato homologado, denominador global da sprint, Q-07 e revisões/documentação oficial do Jira indisponíveis. | PO confirma homologação e disponibiliza o plano. DevOps identifica ambiente e SHA. QA confirma casos planejados, evidências humanas e desempenho. |

[Matriz de riscos](../../qualidade/GP-RiscoBaseadoDefeitos-SetupFlow.xlsx) · [Auditoria da Release 2](../../qualidade/release-2/auditoria-bugs/relatorio-validacao.md)

## 11. Parecer do QA

**Pendente de ajustes para a `main` em `08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`.** A regressão confirma as entregas nominais do incremento, inclusive o fluxo integrado de planejamento. A reprodução do BUG-004 em duas variantes e as duas correções fora desse SHA impedem o parecer de aptidão. O reteste de outra branch complementa a evidência. O merge `c43587c` integrou as duas correções. A reavaliação do parecer para esse SHA depende dos retestes, da CI e das verificações de release indicadas acima. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) A decisão de aceite é do PO.

## 12. Referências e histórico de revisão

- [Registro do ciclo][regressao] e [artefatos][evidencias].
- [Estado das entregas e DoD](../../status-projeto.md), [Plano de Teste versionado](../../qualidade/Plano-de-Teste-SetupFlow.docx), [Plano de Qualidade](../../qualidade/Plano-de-Qualidade-SetupFlow.xlsx) e [Matriz de Riscos](../../qualidade/GP-RiscoBaseadoDefeitos-SetupFlow.xlsx).
- [Relatórios da Sprint 2](README.md#sprint-2), [relatórios da Sprint 3](README.md#sprint-3), [CI][ci] e [workflow](../../../.github/workflows/ci.yml).

| Data | Revisão | Registro |
| --- | --- | --- |
| 26/11/2026 | 1.0 | Ciclo R2-REG-20261126-08a62f5, medições dos drivers e conferência da integração das correções. |
| 26/11/2026 | 1.1 | Estado pós-merge dos BUG-004 e BUG-005. Evidências e parecer do ciclo associados aos SHAs executados. |

[main]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f
[corrigida]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/ee2a4a88aea0018cb451c8f9988346fe25551e7a
[ci]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972
[issue18]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18
[issue19]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19
[issue25]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/25
[issue30]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30
[issue31]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31
[regressao]: ../../qualidade/release-2/regressao-release-2.md
[evidencias]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/README.md
[backend]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/main-pytest/junit.xml
[main-bug004]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/main-fluxo-bug004/stdout.log
[driver01]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/main-driver01-http/amostras.jsonl
[driver04]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/main-driver04-matriz-valida/junit.xml
[driver06]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/main-driver06-http/
[github]: ../../qualidade/release-2/evidencias/regressao-2026-11-26-08a62f5/github.json
