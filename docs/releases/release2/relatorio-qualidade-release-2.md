# Relatório de Qualidade — Release 2

## 1. Identificação

SetupFlow · Release 2 · Sprints 2 e 3 · QA responsável: Leonardo Istamilo. Evidências de 05 a 26/11/2026. Execuções locais automatizadas pelo Codex em 26/11, horário de Brasília (UTC−03:00). Nenhuma tag da Release 2 foi identificada.

| Versão | Evidência |
| --- | --- |
| [`08a62f5`][main] | Regressão R2-REG-20261126-08a62f5 na `main` antes das correções. |
| [`ee2a4a8`][corrigida] | Retestes locais na branch corrigida `docs/qualidade`. |
| [`c43587c`][integrada] | PR #32 integrou as correções à `main`. Mesmos arquivos de backend, frontend e CI da branch retestada. CI e ensaio Q-07 executados neste SHA. |
| [`a5ca0c9`][main-consultada] | Ponta de `origin/main` no checkout consultado nesta revisão. Os commits desde `c43587c` alteraram somente documentação. |

**Ambiente local.** Checkouts isolados, Windows x64 build 26300, Python 3.11.9, PostgreSQL 18.6, Node.js 26.13.0 e Cypress 16.3.0. [Registro de regressão][regressao]

## 2. Resumo executivo

As 11 histórias e os quatro drivers foram integrados e tiveram aceite do PO registrado. O fluxo completo de planejamento passou na regressão local de `08a62f5`. O ciclo também reproduziu os BUG-004 e BUG-005. Os retestes passaram em `ee2a4a8` e as correções entraram em `c43587c`, com **5/5 jobs de CI aprovados**. [Estado das entregas](../../status-projeto.md#release-2) · [Registro de regressão][regressao] · [CI do merge][ci-merge]

**Parecer de QA.** Validação integral da release inconclusiva. As evidências pós-merge confirmam a integração, a CI e a meta de desempenho no cenário local. Dados do plano completo, homologação e casos bloqueados continuam limitando a conclusão. [Parecer](#11-parecer-do-qa)

## 3. Escopo da release

O escopo segue o [registro de entregas](../../status-projeto.md#release-2) e as revisões de cada sprint. A versão integral do plano de testes da Release 2 e o planejamento no Jira ficaram indisponíveis.

| Sprint | Histórias | Drivers |
| --- | --- | --- |
| 2 | [US09](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/10) duração estimada, [US10](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/11) setup direcional, [US12](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/12) planejamento manual, [US26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/9) compatibilidade produto–máquina, [US32](sprint2/relatorio-alinhamento-us32.md) gestão de usuários | [Driver02](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/13), idempotência no cadastro de ordens |
| 3 | [US11](sprint3/relatorio-revisao-pr16-us11.md) matriz de setup, [US13](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/22) sugestão, [US14](../../qualidade/release-2/revisao-us14.md) prazos e prioridades, [US15](../../qualidade/release-2/revisao-us15.md) máquinas elegíveis, [US16](../../qualidade/release-2/revisao-us16.md) comparação, [US17](../../qualidade/release-2/revisao-us17.md) aprovação e consulta | [Driver01](../../qualidade/release-2/revisao-driver01.md) integridade, [Driver04](../../qualidade/release-2/revisao-driver04.md) autorização, [Driver06](../../qualidade/release-2/revisao-driver06.md) sessões expiradas ou invalidadas |

As US01 a US08 e o Driver05 são regressão da Release 1. A execução do Operador no incremento consiste em consultar o plano aprovado. Registro de início e conclusão, replanejamento e indicadores fazem parte da evolução documentada. A cobertura vinculada a esses fluxos está indicada na seção 6.

## 4. Estratégia e cobertura

O ciclo cobriu autenticação, logout, sessão, permissões, usuários, cadastros, ordens, prazos, prioridades, duração, setup direcional, matriz, planejamento e regressão da Release 1. O Pytest e os ensaios reais de API usaram PostgreSQL. O registro identifica os cenários Cypress com respostas simuladas. [Casos e ambiente][regressao]

No **RG-01**, foram cadastrados dados com setups assimétricos, salvos o plano manual e a sugestão e comparadas as duas alternativas (50 e 20 min). A sugestão aprovada persistiu três itens, consultados pelo Operador na mesma sequência. Homologação, execução humana integral e funcionalidades futuras ficaram fora do ciclo. [Evidência do RG-01][main-bug004]

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

| Driver | Meta recuperada das fontes | Método e amostra | Resultado em `08a62f5` | Evidência | Situação |
| --- | --- | --- | --- | --- | --- |
| Driver01 | Reagir corretamente a 100% de ≥20 interrupções, ao menos 10 cadastros e 10 atualizações, preservando os dados confirmados, sem gravação parcial e com indicação da falha | HTTP real em Uvicorn. Encerramento controlado da conexão da transação de teste após escrita e antes do commit. Conferência por outra conexão, com reenvio e controles positivos | 20/20 HTTP 503, 0 gravações parciais, 3/3 controles válidos e 20/20 recuperações | [Amostras][driver01] · [Revisão](../../qualidade/release-2/revisao-driver01.md) | **Atendida para as gravações de ordens disponíveis.** Andamento da execução indisponível para CT-127/128/129 na variante correspondente. |
| Driver02 | 20 operações com resposta perdida após commit e cinco reenvios por operação, mantendo os IDs e sem duplicar ordens. Verificar janela de 24 h, nova chave e concorrência | Pytest com commit real e perda de resposta induzida. Oito testes do driver, incluindo a amostra de 20 cadastros e 100 reenvios. A fronteira usa relógio controlado | Oito testes aprovados. O teste quantitativo exige 20 registros únicos, um por chave, e todos os IDs devolvidos iguais aos IDs persistidos | [Pytest][backend] · [Suíte oficial](../../../backend/testes/integration/drivers/test_driver02_idempotency_ordens.py) | **Atendida no cenário testado.** O ensaio de 24 h simula a passagem do tempo. |
| Driver04 | Bloquear 100% de ≥20 acessos distintos, ao menos 10 de cada condição, sem exposição de dados ou alteração do banco e com controles de Planejador | TestClient + PostgreSQL com dados válidos, incluindo candidatos e aprovação. Comparação de estado antes e depois | 14/14 com Operador (403), 14/14 sem sessão (401), 28/28 sem alteração nem dados protegidos na resposta e 14/14 controles positivos. A suíte oficial passou separadamente em 44 casos. | [Matriz][driver04] · [Revisão](../../qualidade/release-2/revisao-driver04.md) | **Atendida nas rotas disponíveis.** Replanejamento ficou fora da matriz. |
| Driver06 | Rejeitar 100% de ≥20 acessos expirados/invalidados com cada resposta ≤2 s e solicitar nova autenticação. A revisão exige controles de sessão válida e perfil autorizado | Uvicorn/PostgreSQL com expiração gravada no banco e invalidação real por logout. 20 GETs por estado, alternados em oito rotas, e uma escrita adicional por estado. Chrome no fluxo de Famílias | 60/60 GETs devolveram 401, dos quais 20 expirados, 20 invalidados e 20 com token desconhecido como controle. Três escritas retornaram 401 sem gravar. Máximos HTTP de **30,743 ms**, **14,366 ms** e **26,793 ms**, respectivamente. No Chrome, 20/20 recusas, com máximo de **17,3 ms** até a resposta e **19,4 ms** até o formulário. | [HTTP][driver06] · [Revisão](../../qualidade/release-2/revisao-driver06.md) | **Atendida no loopback para os dois marcos medidos.** Aplicabilidade em homologação e interpretação formal do marco continuam a confirmar. |

O Driver06 usa o limite por tentativa. O Driver05 foi revalidado como regressão da Release 1, com 20 ciclos e 200 tentativas adicionais bloqueadas. [Pytest][backend]

## 7. Bugs encontrados e corrigidos

| Registro | Severidade registrada | Fix e integração à `main` | Reteste | Estado da issue |
| --- | --- | --- | --- | --- |
| [BUG-001, #18][issue18], famílias ausentes nos eixos da matriz | Média | `47c63d6` e `bbf29c4`, [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16), merge `8d654d3`. O PR #21 complementou o registro e as evidências | As variantes de origem e destino ausentes passaram no Chrome. [Comentário de QA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18#issuecomment-7109530230) | Fechada |
| [BUG-002, #19][issue19], interface após 401 com identidade indisponível | Média | `67fa646`, [PR #17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/17), merge `a118dcd` | Famílias e Máquinas passaram após HTTP 401 no Chrome. [Comentário de QA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19#issuecomment-7112231551) | Fechada |
| [BUG-003, #25][issue25], distribuição viável rejeitada | Média | `ae8ae27`, [PR #24](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24), merge `db73ab8` | Duas ordens de seleção aprovadas no Pytest. O cenário de redistribuição também passou no Chrome. [Reteste](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/25#issuecomment-7176630592) | Fechada |
| [BUG-004, #30][issue30], aprovação após mudança de elegibilidade | Alta | [`b6c72f2`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/b6c72f2), validada em `ee2a4a8` e integrada em `c43587c` pelo [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) | As duas variantes reprovaram em `08a62f5` com 201 e persistência. Na branch corrigida, 2/2 retornaram 409, sem publicação, e a suíte US17 passou em 13/13. [Reteste anterior](../../qualidade/release-2/auditoria-bugs/reteste-bug004.md) · [Novo ciclo][regressao] | Fechada |
| [BUG-005, #31][issue31], falha temporária na restauração da sessão | Média | [`8978fc1`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/8978fc1), validada em `ee2a4a8` e integrada em `c43587c` pelo [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) | Em `08a62f5`, dois casos reprovaram pela ausência do aviso e da ação de nova tentativa depois do 503. Na branch corrigida, 3/3 retestes integrados e 17/17 cenários oficiais de autenticação passaram. [Reteste anterior](../../qualidade/release-2/auditoria-bugs/reteste-bug005.md) | Fechada |

**Correções internas de PR.** A falha do catálogo que ocultava o plano e impedia abrir a comparação foi corrigida na US16 por `1e98b76`, integrada no PR #27. A referência de usuários aprovadores passou a bloquear exclusão física em `c06fb94`, no PR #28, e o teste de regressão de usuários consta do Pytest. A concorrência da idempotência e a tipagem de UUID foram ajustadas em `c172886`, incluído no PR #17, e a suíte do Driver02 foi exercitada. O tratamento da recusa de sessão na geração de sugestões entrou em `0551a78`, PR #22. Esses registros internos têm rastreio no Git, sem triagem de severidade no conjunto consultado. [Revisão US16](../../qualidade/release-2/revisao-us16.md) · [Pytest][backend] · [Histórico da main][main]

Os ensaios adicionais reproduziram dois defeitos já registrados, sem novos defeitos de produto no recorte executado.

## 8. Verificação da DoD

A matriz detalha os critérios que variam entre entregas. **Atendido** nos testes indica que os testes oficiais ou os retestes pertinentes passaram na versão citada. [DoD vigente](../../status-projeto.md#definition-of-done-dod) · [Mapa de testes][regressao]

| Item e merge | Revisão formal e integração via PR | Critérios validados pelo QA | Testes escritos e passando | Observação |
| --- | --- | --- | --- | --- |
| US09 · #10 `08627f2` | Atendido | Atendido | Atendido | — |
| US10 · #11 `7f93ea6` | Atendido| Atendido | Atendido | — |
| US11 · #16/#21 `8d654d3`/`8f992a1` | Atendido | Atendido | Atendido | — |
| US12 · #12 `49e19c9` | Atendido | Atendido | Atendido | — |
| US13 · #22 `e5d73f1` | Atendido | Atendido | Atendido | — |
| US14 · #23 `39ab129` | Atendido | Atendido | Atendido | CT-115 aprovado após decisão do PO. |
| US15 · #24 `db73ab8` | Atendido | Atendido | Atendido | Critério do CT-119 pendente. |
| US16 · #27 `10cdd8a` | Atendido | Atendido | Atendido | — |
| US17 · #28 `5772ec0` | Atendido | Atendido | Atendido | Falhas em `08a62f5`. Reteste aprovado em `ee2a4a8` e correção integrada. |
| US26 · #9 `a3b6fb2` | Atendido| Atendido | Atendido | — |
| US32 · #15 `5cf655e` | Atendido | Atendido | Atendido | — |
| Driver01 · #26 `65a1d24` | Atendido | Atendido | Atendido | Rollback aprovado para ordens. Andamento indisponível. |
| Driver02 · #13 `aae2669` | Atendido| Atendido | Atendido | — |
| Driver04 · #29 `08a62f5` | Atendido | Atendido | Atendido | Rotas disponíveis validadas. |
| Driver06 · #17 `a118dcd` | Atendido | Atendido | Atendido | Meta medida em loopback. CT-135–137 sem fonte para conclusão por ID. |

Os quatro critérios restantes têm a mesma situação nos 15 itens.

| Critério | Situação | Evidência |
| --- | --- | --- |
| CI sem falhas | Atendido | 5/5 jobs no fechamento pré-merge e no merge das correções. [CI em `08a62f5`][ci] · [CI em `c43587c`][ci-merge] |
| Homologação, quando exigida | Não verificado | A implantação foi informada como pendente. A obrigatoriedade para esta release ficou sem confirmação. |
| Documentação atualizada | Atendido | [Registros das entregas](../../status-projeto.md#release-2) · [Índice da Release 2](README.md) |
| Aceite pelo PO | Atendido | Aceite informado para os 15 itens integrados e registrado no [estado do projeto](../../status-projeto.md#release-2). |

A integração via PR foi confirmada para todos os itens. Na auditoria, 4 dos 16 PRs de entrega tinham revisão formal publicada antes do merge (#10, #22, #27 e #28). A coluna indica **Não verificado** quando falta confirmação do componente de revisão. [Consulta de PRs][github]

## 9. Métricas de qualidade

**Execução (%)** = (aprovados + reprovados) ÷ casos planejados × 100. **Aprovação (%)** = aprovados ÷ (aprovados + reprovados) × 100. Denominador zero resulta em **Não se aplica**. Denominador ou conjunto incompleto é **Não levantado**. Casos do plano, exemplos parametrizados, tentativas de uma medida e repetições em outros navegadores têm unidades próprias.

### A. Histórico das Sprints 2 e 3

| Recorte histórico | Resultado verificável | Limite |
| --- | --- | --- |
| Sprint 2, US32 | 197 Pytest aprovados, 42 da US32 dentro desse total. 32 cenários aprovados por navegador em Chrome e Electron para o conjunto de 12 critérios. O smoke repetiu cinco cenários. [Relatório](sprint2/relatorio-alinhamento-us32.md) | O total de casos planejados e a distribuição de resultados de toda a Sprint 2 ficaram **Não levantados**. |
| Sprint 3, revisões das histórias e dos drivers | Relatórios da US11, US14, US15, US16, US17, Driver01/04/06 e retestes registram datas, commits e escopos diferentes. Em 26/11, a auditoria de `08a62f5` registrou 325 Pytest, 67 Cypress de regressão e 12 de autenticação aprovados, além de dois defeitos exploratórios. [Auditoria anterior](../../qualidade/release-2/auditoria-bugs/relatorio-validacao.md) | A série do mesmo teste entre branches, fases e navegadores permanece separada. Planejados, executados, aprovados, reprovados, bloqueados, não executados e ignorados do plano completo da sprint ficaram **Não levantados**. |

### B. Resultado do ciclo final de regressão

<table>
  <thead>
    <tr>
      <th scope="col">Conjunto em 08a62f5</th>
      <th scope="col">Planejados</th>
      <th scope="col">Executados</th>
      <th scope="col">Aprovados</th>
      <th scope="col">Reprovados</th>
      <th scope="col">Bloqueados</th>
      <th scope="col">Não executados</th>
      <th scope="col">Ignorados</th>
      <th scope="col">Execução</th>
      <th scope="col">Aprovação</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Recorte de IDs do plano rastreados</th><td>48</td><td>41</td><td>41</td><td>0</td><td>7</td><td>0 adicionais</td><td>Não se aplica</td><td>85,42%</td><td>100%</td></tr>
    <tr><th scope="row">Pytest oficial, casos coletados pela ferramenta</th><td>325</td><td>325</td><td>325</td><td>0</td><td>0</td><td>0</td><td>0</td><td>100%</td><td>100%</td></tr>
    <tr><th scope="row">Regressão Cypress, por navegador</th><td>67</td><td>67</td><td>67</td><td>0</td><td>0</td><td>0</td><td>0</td><td>100%</td><td>100%</td></tr>
    <tr><th scope="row">Autenticação oficial Cypress</th><td>12</td><td>12</td><td>12</td><td>0</td><td>0</td><td>0</td><td>0</td><td>100%</td><td>100%</td></tr>
    <tr><th scope="row">RG-01 e BUG-004, ensaios de API</th><td>3</td><td>3</td><td>1</td><td>2</td><td>0</td><td>0</td><td>0</td><td>100%</td><td>33,33%</td></tr>
    <tr><th scope="row">BUG-005 e controle Driver06, ensaio de navegador</th><td>3</td><td>3</td><td>1</td><td>2</td><td>0</td><td>0</td><td>0</td><td>100%</td><td>33,33%</td></tr>
  </tbody>
</table>

Os sete casos bloqueados são CT-119, CT-127–129 e CT-135–137. O recorte aprovou 41/41 casos concluídos. Os ensaios complementares registraram quatro reprovações em dois bugs. Contagens por navegador, ensaios complementares e tentativas dos drivers ficam fora do total de IDs do plano. Os totais do plano integral ficaram **Não levantados**. [Casos e contagens][regressao]

### C. Situação atual da release

Cinco correções de issues públicas estão integradas e têm reteste aprovado (1 alta, 4 médias). As cinco issues consultadas estão fechadas. O total de bugs abertos no Jira ficou **Não levantado**. [Detalhes](#7-bugs-encontrados-e-corrigidos)

O fechamento informou atendimento das nove metas. A auditoria confirmou Q-07 no ensaio local e registrou os limites das demais evidências, incluindo 41/48 casos executados no recorte, 4/16 PRs com revisão formal e CI verde no merge. [Métricas declaradas e evidências](relatorio_metricas_qualidade_riscos.md#2-consolidação-das-métricas)

### Q-07 — Teste de carga e tempo de resposta

**Meta atendida no ensaio local em `c43587c`.** Com k6 2.4.0, 2.280 ordens e API e PostgreSQL em loopback, foram executadas duas rodadas de 3 min após 30 s de aquecimento. Houve 594 amostras por operação com 5 usuários virtuais (VUs) e 649 com 10 VUs, sem falhas de requisição ou validação. O limite de p95 foi 2.000 ms por operação e por rodada.

| Operação | p95 com 5 VUs (ms) | p95 com 10 VUs (ms) |
| --- | ---: | ---: |
| Consultar ordens | 331,07 | **1.083,27** |
| Matriz de setup, famílias | 213,82 | 589,03 |
| Matriz de setup, tempos | 185,26 | 610,95 |
| Gerar sugestão | 227,30 | 661,63 |
| Comparar manual e sugerido | 135,48 | 466,95 |
| Aprovar sugestão | 175,80 | 521,39 |
| Consultar aprovados | 188,91 | 590,21 |

O ensaio mediu requisições HTTP locais. A UI, a rede externa e os patamares do plano de riscos R-07 a R-09 ficaram fora das condições medidas. [Manifesto e comandos][q07] · [Resultados de 5 VUs](../../qualidade/release-2/evidencias/q07/2026-11-26-c43587c/resultados-medicao-5-vus.json) · [Resultados de 10 VUs](../../qualidade/release-2/evidencias/q07/2026-11-26-c43587c/resultados-medicao-10-vus.json)

## 10. Riscos e limitações

- **Cobertura pendente.** QA precisa da íntegra do plano para os totais e casos sem fonte. O PO precisa confirmar o resultado esperado do CT-119. A revisão da US14 registra falha histórica de downgrade após persistir uma sugestão. Este ciclo verificou a migração de subida. [Registro do ciclo][regressao] · [Revisão US14](../../qualidade/release-2/revisao-us14.md#downgrade-falha-após-gravar-sugestão-válida-com-aumento-de-setup)
- **Ambiente.** Falhas anteriores de memória do Argon2 e timeout operacional do Chrome passaram em repetições sequenciais e ficaram sem recorrência nos logs deste ciclo. A espera do BUG-005 em `08a62f5` expirou na asserção do aviso de recuperação. [Registro do ciclo][regressao]
- **Validação da entrega.** PO e DevOps precisam confirmar a exigência de homologação. A [matriz de métricas e riscos](relatorio_metricas_qualidade_riscos.md#3-avaliação-dos-riscos-da-release) reúne os riscos de desempenho, concorrência e autorização com evidência parcial.

## 11. Parecer do QA

**Pendente de ajustes em `08a62f5`**, versão pré-merge em que quatro casos complementares reprovaram ao reproduzir dois bugs conhecidos.

**Validação inconclusiva para o fechamento técnico em `c43587c`.** As correções foram integradas após retestes específicos aprovados em `ee2a4a8`, a CI passou e o ensaio local Q-07 atingiu a meta no SHA integrado. A regressão local completa permanece registrada em `08a62f5`. A cobertura integral depende dos casos bloqueados, das fontes do plano e da confirmação da etapa de homologação. O aceite das entregas pelo PO está registrado separadamente. [Registro de regressão][regressao] · [PR #32][pr32] · [CI do merge][ci-merge]

## 12. Referências e histórico de revisão

- [Registro do ciclo][regressao] e [artefatos][evidencias].
- [Estado das entregas e DoD](../../status-projeto.md), [Plano de Teste versionado](../../qualidade/Plano-de-Teste-SetupFlow.docx), [Plano de Qualidade](../../qualidade/Plano-de-Qualidade-SetupFlow.xlsx) e [Matriz de Riscos](../../qualidade/GP-RiscoBaseadoDefeitos-SetupFlow.xlsx).
- [Relatórios da Sprint 2](README.md#sprint-2), [relatórios da Sprint 3](README.md#sprint-3), [CI][ci] e [workflow](../../../.github/workflows/ci.yml).

| Data | Revisão | Registro |
| --- | --- | --- |
| 26/11/2026 | 1.0 | Ciclo R2-REG-20261126-08a62f5, medições dos drivers e conferência da integração das correções. |
| 26/11/2026 | 1.1 | Estado pós-merge dos BUG-004 e BUG-005. Evidências e parecer do ciclo associados aos SHAs executados. |
| 26/11/2026 | 1.2 | Ensaio local de carga e resultados da Q-07 no SHA integrado. |
| 26/11/2026 | 1.3 | Atualização dos nove indicadores conforme o plano de qualidade de fechamento da Release 2. |
| 26/11/2026 | 1.4 | Revisão de consistência entre versões, DoD, métricas e parecer. |

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
[integrada]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/c43587c653ede3d3438bdf780657e1c15624a6bc
[main-consultada]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/a5ca0c9727416a9d1381b9a28df4ef342d2a0303
[ci-merge]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45882475010
[pr32]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32
[q07]: ../../qualidade/release-2/evidencias/q07/2026-11-26-c43587c/manifesto.json
