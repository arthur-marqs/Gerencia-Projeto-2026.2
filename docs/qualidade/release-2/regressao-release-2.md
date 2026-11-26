# Registro de regressão — Release 2

## Identificação do ciclo

**Atualização pós-merge.** As correções entraram na `main` em `c43587c`. As reproduções e os retestes deste registro foram executados em `08a62f5` e `ee2a4a8`, respectivamente. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32)

| Campo | Registro |
| --- | --- |
| Ciclo e fuso | R2-REG-20261126-08a62f5, 26/11/2026, America/Sao_Paulo (UTC−03:00) |
| QA da Release 2 | Leonardo Istamilo, conforme a organização do projeto |
| Execução deste ciclo | Automação pelo Codex. O ciclo não incluiu validação humana. |
| Versão alvo | `origin/main` em `08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`, única versão integrada identificada |
| Versão complementar | `origin/docs/qualidade` em `ee2a4a88aea0018cb451c8f9988346fe25551e7a`, com os fixes `b6c72f2` e `8978fc1` |
| Estado das cópias | Dois clones locais em HEAD destacado. A branch original foi preservada. Campos de estado por comando no [manifesto][manifesto]. |
| Ambiente | Windows x64 build 26300, oito processadores lógicos e 7,80 GiB de RAM física visível. Python 3.11.9, pytest 8.4.2, FastAPI 0.162.0, SQLAlchemy 2.1.6, psycopg 3.3.6, Argon2 25.1.0, PostgreSQL 18.6, Node 26.13.0, npm 11.20.0, Cypress 16.3.0 e Chrome 158.0.8127.38. Electron 150.0.7871.250. [Inventário de versões](evidencias/regressao-2026-11-26-08a62f5/ambiente.json) |
| Tag | A consulta de referências encontrou apenas `v0.1.0`, da Release 1. [Consulta do GitHub][github] |

## Escopo e dados de teste

O ciclo cobre cadastros e acesso da Release 1 afetados pelo incremento, US09/10/12/26/32 e Driver02 da Sprint 2 e US11/13–17 e Drivers01/04/06 da Sprint 3. A seleção foi baseada no [escopo de entrega](../../status-projeto.md#release-2), no [plano de qualidade](../Plano-de-Qualidade-SetupFlow.xlsx), nos relatórios e na matriz citada pela [auditoria anterior](auditoria-bugs/relatorio-validacao.md). O DOCX de teste versionado cobre a Release 1. O anexo da Release 2, com revisão 2.4 citada na auditoria, ficou indisponível para consulta direta. O Jira também ficou indisponível. A rastreabilidade abaixo usa os trechos e critérios preservados nas evidências.

- PostgreSQL descartável em `127.0.0.1:55483`, com autenticação SCRAM. Os bancos `release2_main_test`, `release2_main_e2e_test`, `release2_corrigida_test` e `release2_corrigida_e2e_test` separam Pytest e navegador por versão. `release2_driver_test` é dedicado ao ensaio de desconexão. As migrações foram aplicadas antes dos cenários. A API e o Vite preview usaram as portas locais 8000 e 5173.
- A massa usa contas sintéticas de Planejador, Operador e Administrador, com produtos, famílias, ordens e máquinas de fixture. Os ganchos do Cypress reinicializam apenas o banco E2E. A regressão de navegador usa um build do checkout testado. Os testes de autenticação que controlam respostas da API e a falha pontual de catálogo da US16 exercitam o comportamento de tela. Os ensaios de autorização, sessão e persistência usam PostgreSQL real.
- As suítes com uso intensivo de recursos rodaram em sequência. Parâmetros do Argon2, asserções, filtros das suítes oficiais e timeouts dos testes oficiais foram preservados. `COOKIE_SECURE=false` segue o guia para HTTP no loopback. A opção de vídeo do Cypress foi desativada para limitar uso de recursos. Os relatórios estruturados e as falhas foram preservados.
- A política do lote misto, a aplicabilidade da homologação, o inventário global do plano e o escopo de execução de ordens continuam abertos. Ficam fora do recorte a carga de Q-07, o downgrade da US14 com dados, a validação em homologação e a execução manual em nome do QA da equipe.

## Comandos e execuções

Os comandos abaixo são abreviados com `python` para o executável 3.11 e `npm` para o binário local de Node. A execução e os horários de início e fim, o commit, os argumentos, o resultado do processo e as durações estão no [manifesto][manifesto]. O caderno de [evidências][evidencias] contém JUnit, resumos do Cypress, logs saneados e medições individuais. Os comandos com ensaios avulsos são executados na pasta indicada pelo manifesto e usam apenas bancos descartáveis.

| Execução | Comando ou procedimento |
| --- | --- |
| Backend oficial | `python -m pytest -q --tb=short --junitxml=<caminho> testes` a partir de `backend` |
| RG-01 e BUG-004 em ambas as versões | `python -m pytest -q --tb=short -s -o junit_family=xunit1 -p testes.integration.conftest <casos>/test_qa_ciclo.py --junitxml=<caminho>` |
| Driver01 HTTP | `python <repositório>/docs/qualidade/release-2/evidencias-driver01/qa_desconexao.py`, a partir de `backend` com `TEST_DATABASE_URL` no banco dedicado |
| Driver04 complementar | `python -m pytest -q --tb=short -o junit_family=xunit1 -p testes.integration.conftest <casos>/test_qa_matriz.py --junitxml=<caminho>` |
| Driver06 por HTTP | `python -m pytest -q --tb=short -s -p testes.integration.conftest <casos>/test_qa_driver06_http.py --junitxml=<caminho>`, com Uvicorn local |
| Driver06 no Chrome | `python -m scripts.seed_e2e normal`, Chrome descartável e `node <casos>/qa-sessao.mjs <amostras.json> --medir-driver06` |
| Regressão frontend | `npm run test:e2e:regressao -- --browser chrome` e `npm run test:e2e:regressao -- --browser electron` |
| Login e sessão | `npm run test:e2e:login -- --browser chrome` |
| BUG-005 integrado | Cypress via CLI com a mesma spec auxiliar de três cenários nas duas versões, apoiada em login real e PostgreSQL local. A configuração temporária cria a massa e expira a sessão da fixture. |
| US17 com correções | `python -m pytest -q --tb=short --junitxml=<caminho> testes/integration/test_us17_aprovacao.py` |
| Validações complementares | `npm run lint`, `npm run build` e `python -m alembic upgrade head`. A API e o build foram servidos localmente para o Cypress. |

## Rastreabilidade dos casos e resultados

Os intervalos em itálico na coluna Caso correspondem a IDs de um mesmo grupo. Os 48 IDs abaixo marcados como plano são 12 de gestão de usuários (CT-32–43), três de idempotência (CT-94–96) e 33 da Sprint 3 (CT-105–137). Essa é uma seleção rastreável, sem afirmar que seja o inventário completo da Release 2. Os casos auxiliares e de regressão da Release 1 aparecem em linhas próprias, fora desse denominador.

| Caso | US ou driver | Cenário | Tipo de execução | Resultado na `main` | Evidência | Bug relacionado |
| --- | --- | --- | --- | --- | --- | --- |
| Plano *CT-32–43* | US32 | Gestão de usuários, perfis, contas, senhas, desativação, concorrência e vínculos históricos | Cypress e Pytest | Aprovado, 12 IDs correspondentes a 32 exemplos no Chrome. A suíte da US32 contém 44 integrações de backend. | [Roteiro](../../releases/release2/sprint2/roteiro-testes-us32.md) · [Cypress][chrome] · [Pytest][backend] | Exclusão de aprovadores, ajuste `c06fb94` |
| Plano *CT-94–96* | Driver02 | Reenvio, prazo de retenção, chaves novas e concorrência, no conjunto documentado | Pytest e banco real, relógio controlado na fronteira | Aprovado no conjunto rastreado | [Pytest][backend] · [Auditoria](auditoria-bugs/relatorio-validacao.md#drivers) | Concorrência de idempotência |
| Plano *CT-105–106* | US11 | Direção da matriz, estado vazio e famílias ausentes nos eixos | Cypress, resposta de lista controlada nas variantes do bug | Aprovado, quatro cenários no Chrome. | [Cypress][chrome] · [QA](../../releases/release2/sprint3/relatorio-revisao-pr16-us11.md) | BUG-001 |
| Plano *CT-107–112* | US13 | Geração, seleção, ordem, empate, recuperação, vazio e mesma família | Cypress e Pytest | Aprovado, 13 cenários no Chrome, incluindo regressões adicionais CT-79–85. | [Cypress][chrome] · [Pytest][backend] | — |
| Plano *CT-113–115* | US14 | Prazo antes de setup com prioridade igual, alta urgente e antecipação de baixa condicionada | Cypress e Pytest | Aprovado, seis cenários no Chrome, incluindo os dois exemplos do CT-115. | [Cypress][chrome] · [Regra aprovada](revisao-us14.md#reavaliação-após-a-decisão-do-po) | Downgrade em risco separado |
| Plano *CT-116–118* | US15 | Atribuição, distribuição, recusa de máquina incompatível ou inativa | Pytest e Cypress | Aprovado no conjunto rastreado. A suíte tem cinco cenários no Chrome, incluindo CT-119 e BUG-003 em linhas próprias. | [Cypress][chrome] · [Pytest][backend] | BUG-003 retestado em linha própria |
| Plano CT-119 | US15 | Lote misto com ordem sem máquina elegível | Pytest e Cypress | Bloqueado para conclusão de aceite. A API implementa HTTP 422 sem gravar em lote misto. A política esperada precisa de confirmação. | [QA](revisao-us15.md#rastreabilidade-da-reavaliação) · [Pytest][backend] · [Cypress][chrome] | — |
| Plano *CT-120–122* | US16 | Comparar, orientar sem sugestão e preservar fontes | Pytest e Cypress | Aprovado. | [Pytest][backend] · [Cypress][chrome] | Catálogo 503 verificado à parte |
| Plano *CT-123–125* | US17 | Aprovação nominal, ausência de candidatos, escolha da origem e consulta persistida | Pytest e Cypress | Aprovado, três cenários no Chrome. As reprovações do BUG-004 são cenários adicionais de mudança de elegibilidade. | [Pytest][backend] · [Cypress][chrome] | BUG-004 |
| Plano CT-126 | Driver01 | 10 cadastros com interrupção após a escrita e antes do commit | HTTP real e comparação por outra conexão | Aprovado, 10/10 cadastros sem gravação parcial | [Amostras][driver01] | — |
| Plano *CT-127–129* | Driver01 | 10 mutações de campos, três controles positivos e reenvios. Inclui variante de alteração de andamento no plano citado. | HTTP real | Bloqueado para conclusão integral. As gravações e reenvios disponíveis passaram. A variante de andamento ficou sem execução, por indisponibilidade da operação. | [Amostras][driver01] · [Escopo](revisao-driver01.md#3-rastreabilidade) | — |
| Plano *CT-130–132* | Driver04 | Negativas para Operador e sem sessão, com dados válidos e controles de Planejador | TestClient e banco real | Aprovado para as rotas disponíveis, 14×3. Replanejamento futuro ficou fora da matriz. | [Matriz][driver04] | — |
| Plano *CT-133–134* | Driver06 | Expiração e invalidação, recusa e retorno ao login | HTTP real e navegação medida | Aprovado. 20/20 recusas por estado no HTTP e 10/10 por estado no Chrome, todos abaixo de 2 s nos marcos de resposta e formulário. | [Desempenho por tentativa][driver06] · [Autenticação][auth] | BUG-002 |
| Plano *CT-135–137* | Driver06 | Controles adicionais referenciados no plano citado | Evidências funcionais de sessão válida e perfis, mais teste de expiração no Pytest | Bloqueado para conclusão por ID. A associação individual aos três critérios depende da íntegra do plano. | [Revisão do Driver06](revisao-driver06.md#3-rastreabilidade-da-reavaliação) · [Pytest][backend] | — |
| Regressão da Release 1 | US01–US08, Driver05 | Login, logout, sessão, permissões, cadastros e 20 ciclos de bloqueio com 200 tentativas extras | Pytest e Cypress | Cobertura nominal aprovada na automação oficial. O BUG-005 foi exercitado em ensaio próprio. | [Pytest][backend] · [Autenticação][auth] | BUG-005 |
| S2 complementar | US09/10/12/26 | Duração, tempos por direção, montagem manual, compatibilidades e persistência | Pytest | Aprovado | [Pytest][backend] | — |
| RG-01 | US10/12/13/16/17 | Preparar A/B/A → selecionar → salvar manual → sugerir → comparar → aprovar → consultar como Operador | TestClient + PostgreSQL real | Aprovado. Manual 50 min, sugestão 20 min, diferença −30 min, 3 itens e consulta 200. | [Amostra][bug004] · [Fonte do ensaio][fluxo] | — |
| BUG-001 | US11 | Origem e destino ausentes, tempos direcionais e contador | Cypress com lista de famílias controlada | Aprovado, 2/2 variantes no Chrome. | [Cypress][chrome] | [#18][issue18] |
| BUG-002 | Driver06 | 401 em Famílias e Máquinas com identidade configurada para 503 | Cypress, respostas controladas. Segurança da API verificada na medição HTTP real. | Aprovado, 2/2 variantes no Chrome. | [Autenticação][auth] · [HTTP][driver06] | [#19][issue19] |
| BUG-003 | US15 | Redistribuir ordens sem setup disponível na primeira atribuição, em ambas as ordens de seleção | Pytest parametrizado e Cypress | Duas variantes de API aprovadas. Cenário de interface aprovado no Chrome. | [Pytest][backend] · [Cypress][chrome] | [#25][issue25] |
| BUG-004 | US17/US15 | Máquina desativada e vínculo removido após geração, antes da aprovação | API e banco real | Reprovado em 2/2. Em cada variante, 201, uma aprovação, um item e um plano visível ao Operador. O reteste na branch corrigida retornou 409, com zero gravações, nas duas variantes. | [Main][bug004] · [Corrigida][corrigida-004] | [#30][issue30] |
| BUG-005 | US01/Driver06 | Consulta de identidade inicial 503, recuperação 200 com sessão válida, sessão expirada 401 e identidade atrasada | Cypress com sessão e chamadas reais, exceto injeções de 503 e identidade tardia | Na main, 2 reprovados e 1 aprovado. Na cópia corrigida, os 3 casos passaram. | [Main][bug005] · [Corrigida][corrigida-005] | [#31][issue31] |
| Catálogo 503 | US16 | Comparação e ordens visíveis enquanto catálogo indisponível | Cypress com 503 controlado somente no catálogo | Aprovado no Chrome. | [Cypress][chrome] | Ajuste `1e98b76`, PR #27 |

### Resultados por suíte

| Versão | Execução | Horário BRT | Duração do comando | Saída | Resultado e evidência |
| --- | --- | --- | ---: | ---: | --- |
| `08a62f5` | Pytest oficial | 15:29:07–15:32:28 | 201,09 s | 0 | 325/325 aprovados, 0 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-pytest/) |
| `08a62f5` | RG-01 e BUG-004 | 15:32:51–15:32:57 | 6,08 s | 1 | 1/3 aprovados, 2 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-fluxo-bug004/) |
| `08a62f5` | Driver01 HTTP | 15:32:57–15:33:14 | 17,56 s | 0 | 20/20 falhas tratadas, 3/3 controles e 20/20 reenvios. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-driver01-http/) |
| `08a62f5` | Matriz Driver04 | 15:33:14–15:33:58 | 43,73 s | 0 | 42/42 aprovados, 0 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-driver04-matriz-valida/) |
| `08a62f5` | Driver06 HTTP | 15:33:58–15:34:08 | 10,17 s | 0 | 3/3 testes, 60 recusas GET e 3 POST. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-driver06-http/) |
| `ee2a4a8` | RG-01 e BUG-004 | 15:34:08–15:34:18 | 9,25 s | 0 | 3/3 aprovados, 0 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-fluxo-bug004/) |
| `ee2a4a8` | Pytest US17 | 15:34:18–15:34:36 | 18,16 s | 0 | 13/13 aprovados, 0 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-us17/) |
| `08a62f5` | Lint | 15:34:36–15:34:49 | 12,76 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-lint/) |
| `08a62f5` | Build | 15:34:49–15:34:59 | 10,60 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-build/) |
| `08a62f5` | Migrações E2E | 15:34:59–15:35:02 | 2,71 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-alembic/) |
| `08a62f5` | Cypress regressão Chrome | 15:35:05–15:43:21 | 495,85 s | 0 | 67/67 aprovados, 0 falhas, 0 erros, 0 ignorados, 0 pendentes. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-regressao-chrome/) |
| `08a62f5` | Cypress autenticação Chrome | 15:43:21–15:43:46 | 25,42 s | 0 | 12/12 aprovados, 0 falhas, 0 erros, 0 ignorados, 0 pendentes. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-auth-chrome/) |
| `08a62f5` | Driver06 Chrome | 15:43:48–15:44:05 | 16,27 s | 0 | 20/20 recusas e retorno ao login. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-driver06-chrome/) |
| `08a62f5` | BUG-005 integrado | 15:44:05–15:44:43 | 37,82 s | 2 | 1/3 aprovados, 2 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-bug005-integrado/) |
| `ee2a4a8` | Lint | 15:44:43–15:44:55 | 11,76 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-lint/) |
| `ee2a4a8` | Build | 15:44:55–15:45:05 | 10,10 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-build/) |
| `ee2a4a8` | Migrações E2E | 15:45:05–15:45:08 | 3,41 s | 0 | Concluído. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-alembic/) |
| `ee2a4a8` | Cypress autenticação Chrome | 15:45:12–15:45:44 | 31,77 s | 0 | 17/17 aprovados, 0 falhas, 0 erros, 0 ignorados, 0 pendentes. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-auth-chrome/) |
| `ee2a4a8` | BUG-005 integrado | 15:45:44–15:46:09 | 24,73 s | 0 | 3/3 aprovados, 0 falhas, 0 erros, 0 ignorados. [Evidência](evidencias/regressao-2026-11-26-08a62f5/corrigida-bug005-integrado/) |
| `08a62f5` | Cypress regressão Electron | 15:46:15–15:53:18 | 423,06 s | 0 | 67/67 aprovados, 0 falhas, 0 erros, 0 ignorados, 0 pendentes. [Evidência](evidencias/regressao-2026-11-26-08a62f5/main-regressao-electron/) |

Os relatórios distinguem reprovações de produto, falhas de preparação e casos com status `skipped` ou `pending`. As durações de ferramenta e de comando são independentes. Os testes repetidos em mais de um navegador ou na outra versão continuam representados por execução.

## Falhas, investigação e reexecuções

- **Preparação do ambiente.** O executável Python 3.11 da Microsoft Store ficou indisponível no sandbox. A tentativa com 3.12 não importou extensões compiladas para 3.11. O ciclo usou o Python 3.11 com as dependências versionadas e autorização de execução. A primeira invocação de `initdb` teve erro de passagem do parâmetro `--pwfile`. Após inicializar o banco, `pg_ctl` não conseguiu criar o processo Windows no sandbox. O processo PostgreSQL do banco descartável foi iniciado diretamente em loopback. Uma partida do executor foi interrompida pela verificação de propriedade do clone Git. A exceção de `safe.directory` foi limitada aos dois clones, no processo. Esses eventos ocorreram antes dos testes da versão.
- **Produto, BUG-004.** Asserções esperavam 409, exclusão dos candidatos e nenhuma gravação. A `main` retornou 201 com persistência confirmada em consulta independente, nas duas condições. A mesma spec em `ee2a4a8` passou. A execução original está preservada e as contagens continuam separadas. [Main][bug004] · [Corrigida][corrigida-004]
- **Produto, BUG-005.** A primeira consulta recebeu o 503 controlado. Dois casos atingiram o limite de espera da asserção porque o aviso de recuperação não apareceu, com saída 2. A variante de expiração durante a nova tentativa ficou interrompida antes desse passo. O controle de resposta tardia após 401 real passou na main. Os três casos passaram na cópia corrigida, incluindo sessão válida com 200 e sessão expirada com 401. [Main][bug005] · [Corrigida][corrigida-005]
- **Histórico de ambiente.** O [reteste da US16](revisao-us16.md#reteste-da-correção-do-catálogo) teve falha de alocação de memória do Argon2 na massa do CT-85. O [reteste do BUG-005](auditoria-bugs/reteste-bug005.md) registrou a falha na massa do CT35, e o [BUG-004](auditoria-bugs/reteste-bug004.md) registrou erros de memória e timeout do Chrome na rodada paralela. As repetições isoladas e sequenciais passaram nas respectivas versões históricas. No ciclo novo, as suítes oficiais passaram na primeira execução sequencial sem nova assinatura de erro de memória do Argon2 ou timeout operacional. Os dois timeouts de asserção no BUG-005 foram mantidos como falhas de produto.

## Conclusão e limitações

**Parecer do ciclo pré-merge em `08a62f5`: Pendente de ajustes.** O fluxo integrado nominal passou e o BUG-004 foi reproduzido. O BUG-005 também foi reproduzido na restauração. As suítes oficiais passaram em Chrome e Electron. Os retestes específicos passaram no checkout que contém os fixes. As medições locais apoiam o parecer no escopo exercitado. O PR #32 integrou as correções em `c43587c`. Este ciclo se refere às versões pré-merge. O fechamento da release depende da validação aplicável ao SHA integrado. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) [Relatório de Qualidade](../../releases/release2/relatorio-qualidade-release-2.md)

[evidencias]: evidencias/regressao-2026-11-26-08a62f5/README.md
[manifesto]: evidencias/regressao-2026-11-26-08a62f5/manifesto.json
[github]: evidencias/regressao-2026-11-26-08a62f5/github.json
[backend]: evidencias/regressao-2026-11-26-08a62f5/main-pytest/junit.xml
[chrome]: evidencias/regressao-2026-11-26-08a62f5/main-regressao-chrome/run-summary.json
[auth]: evidencias/regressao-2026-11-26-08a62f5/main-auth-chrome/run-summary.json
[bug004]: evidencias/regressao-2026-11-26-08a62f5/main-fluxo-bug004/junit.xml
[corrigida-004]: evidencias/regressao-2026-11-26-08a62f5/corrigida-fluxo-bug004/junit.xml
[bug005]: evidencias/regressao-2026-11-26-08a62f5/main-bug005-integrado/
[corrigida-005]: evidencias/regressao-2026-11-26-08a62f5/corrigida-bug005-integrado/
[driver01]: evidencias/regressao-2026-11-26-08a62f5/main-driver01-http/amostras.jsonl
[driver04]: evidencias/regressao-2026-11-26-08a62f5/main-driver04-matriz-valida/junit.xml
[driver06]: evidencias/regressao-2026-11-26-08a62f5/main-driver06-http/
[fluxo]: evidencias/regressao-2026-11-26-08a62f5/ensaios/test_qa_ciclo.py
[issue18]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18
[issue19]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19
[issue25]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/25
[issue30]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30
[issue31]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31
