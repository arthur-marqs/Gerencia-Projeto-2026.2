# Relatório de validação e auditoria de bugs — SetupFlow R2

**Estado em 26/11/2026.** O PO aceitou as histórias e os drivers já integrados à `main`. A auditoria deste commit encontrou dois defeitos. As correções passaram nos retestes em `docs/qualidade` e aguardam integração. [Estado das entregas e DoD](../../../status-projeto.md) · [Acompanhamento dos defeitos](README.md)

**Atualização em 26/11/2026** — As correções do BUG-004 e do BUG-005 foram validadas localmente nos códigos de `b6c72f2` e `8978fc1`. O parecer acima continua associado ao commit da auditoria original. [Reteste do BUG-004](reteste-bug004.md) · [Reteste do BUG-005](reteste-bug005.md)

## 1. Escopo e fontes

A auditoria cobre as Sprints 2 e 3 da Release 2. O escopo de teste inclui duração estimada, configuração e matriz de setup, planejamento manual, sugestão, compatibilidade produto–máquina, prazos e prioridades, comparação, aprovação e gestão de usuários. Foram avaliados os Drivers01, 02, 04 e 06 e as regressões pertinentes da R1, incluindo autenticação, perfis, cadastros, ordens e Driver05. Na execução da produção, o escopo entregue é a consulta às sequências aprovadas. O registro de andamento e o replanejamento completo seguem pendentes de cobertura conforme o plano. A execução de indicadores e os itens de R3/R4 ficaram fora do escopo.

- O `Plano-de-Teste-SetupFlow-3.md`, fornecido para a Release 2, tem revisão **2.4 de 23/11/2026** no histórico e ainda exibe **2.3 / Sprint 2** na identificação. Foram usadas as seções de ambas as sprints, incluindo CT-105 a CT-137. O documento de releases atualizado foi usado como referência de planejamento. O escopo efetivamente integrado foi conferido pelo Git e pela CI.
- O `Plano_de_Qualidade_SetupFlow.xlsx` define Q-01 a Q-09. A cópia mais recente encontrada de `Definition_of_Done_Sprint_Release_SetupFlow(2).xlsx` tem registro preenchido para a R1 e inclui os critérios de homologação, regressão, versão publicada e drivers para o fechamento de release. A vigência dessas cópias no Jira ficou sem comprovação.
- Foram lidos os guias de execução, a arquitetura, a política de testes e as revisões por item. A busca no checkout e nos diretórios superiores aplicáveis ficou sem resultado para `AGENTS.md`. [README do projeto](../../../../README.md) · [Backend](../../../../backend/README.md) · [Cypress](../../../../frontend/cypress/README.md) · [Arquitetura](../../../arquitetura/arquitetura.md) · [Workflow](../../../../.github/workflows/ci.yml)
- No GitHub foram consultados a `main`, as três issues históricas, PRs, revisões, releases públicas e a CI em modo de leitura. [Inventário da consulta](evidencias/github-integracao.json)

## 2. Versão e ambiente

| Campo | Registro |
|---|---|
| Data | 26/11/2026, America/Sao_Paulo |
| Branch | `docs/qualidade`, no mesmo commit de `origin/docs/qualidade`, `origin/main` e da `main` consultada no GitHub |
| Commit | [`08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f), merge do PR [#29](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/29) |
| Alterações locais | Checkout limpo no início. Os documentos e ensaios avulsos da auditoria foram acrescentados depois, sem alterações no produto ou nas suítes oficiais. |
| Ambiente | Windows 11 26H2, build 26300, Python 3.11.9, PostgreSQL 18.6, Node 26.13.0, Vite 8.3.5, Chrome 158.0.8127.38 e Cypress 16.3.0 |
| Isolamento | PostgreSQL descartável em loopback, três bancos dedicados `*_test`, fixtures e contas sintéticas, migrações aplicadas até `8d17b4f2c306`. As medições de rollback e sessão usaram Uvicorn em loopback. O navegador usou o frontend compilado por Vite. |

## 3. Execuções e evidências

| Execução | Tipo | Resultado | Evidência |
|---|---|---|---|
| Pytest oficial | Testes unitários e integração FastAPI TestClient + PostgreSQL | **325 aprovados**, 0 falhas, 0 erros e 0 pulados, em 222,83 s. Há 23 unitários e 302 testes de integração. | [Inventário por caso](evidencias/pytest-resumo.json) |
| Cypress regressão e autenticação | Chrome. Regressão com frontend, API e PostgreSQL locais. Autenticação tem cenários de interface com respostas simuladas. | **67/67** na regressão e **12/12** em autenticação, dos quais 7 do Driver06 e 5 de login. Zero falhas, pendências ou saltos. Os 67 incluem respostas simuladas pontuais na matriz e na comparação. | [Regressão](evidencias/cypress-regressao.json) · [Autenticação](evidencias/cypress-auth.json) |
| Build do frontend | Compilação local | `npm run build` concluído. | [Job de lint e build no mesmo SHA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972/job/139933975439) |
| Driver01 | HTTP real, desconexão PostgreSQL após escrita em transação | 20/20 respostas de falha com estado preservado, 3/3 controles positivos e 20/20 recuperações em ordens. | [Amostras individuais](evidencias/driver01-rollback.json) |
| Driver04 | TestClient, PostgreSQL e comparação de linhas persistidas | 36/36 da matriz versionada e 6/6 do complemento de aprovação. Total de 28 negativas distintas e 14 controles positivos. | [Casos e resultados](evidencias/pytest-resumo.json) · [Complemento da US17](evidencias/test_qa_aprovacao_permissoes.py) |
| Driver06, API e fronteira | HTTP real Uvicorn + PostgreSQL. TestClient e relógio controlado somente para o limite de expiração. | 60/60 recusas na API, 3 escritas recusadas sem persistência e fronteira 3/3. | [Expirada](evidencias/driver06-http-expirada.json) · [Invalidada](evidencias/driver06-http-invalidada.json) · [Desconhecida](evidencias/driver06-http-desconhecida.json) · [Fronteira](evidencias/pytest-resumo.json) |
| Driver06, navegador | Chrome, Uvicorn e PostgreSQL reais, com observação do corpo da resposta e do formulário. Sem respostas simuladas. | 20/20 recusas e retorno ao login, 10 por condição. Máximo de **12,6 ms** até a resposta completa e **13,7 ms** até o formulário. | [Medições no Chrome](evidencias/driver06-browser.json) · [Script](evidencias/qa-sessao.mjs) |
| Exploração de aprovação | TestClient, PostgreSQL, autenticação dos dois perfis | O defeito ocorreu em 2/2 variantes. | [Resultados](evidencias/aprovacao-maquina-inelegivel.json) |
| Exploração de restauração da sessão | Chrome, sessão real, primeira consulta com 503 simulado | O defeito ocorreu em 3/3 tentativas. | [Resultados](evidencias/sessao-identidade-503.json) |
| CI em `main` | Backend, Cypress Chrome e Electron, autenticação, lint e build | Cinco jobs com sucesso no push do SHA auditado. Os logs brutos dos jobs retornaram HTTP 403 na consulta sem credencial. O workflow, os status dos passos e a reprodução local sustentam o registro da cobertura. | [CI do SHA](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972) |

Para reproduzir as execuções, configure `TEST_DATABASE_URL` para PostgreSQL local descartável com nome terminado em `_test`. Use um banco separado para cada execução concorrente. Para Cypress, aplique as migrações e configure `E2E_DATABASE_URL` para um banco dedicado terminado em `_e2e_test`. Inicie a API e a UI conforme os guias. Os testes de sessão precisam permitir cookies no HTTP local. Os scripts históricos do Driver06 foram copiados para a pasta ignorada `.tmp/qa-release2-08a62f5` antes da execução porque gravam evidência ao lado do script. [Guia do backend](../../../../backend/README.md) · [Guia do Cypress](../../../../frontend/cypress/README.md)

```sh
# A partir de backend
python -m pytest -q --tb=short --junitxml=../.tmp/qa-release2-08a62f5/pytest.xml testes
python ../docs/qualidade/release-2/evidencias-driver01/qa_desconexao.py
python -m pytest -q -p testes.integration.conftest ../docs/qualidade/release-2/evidencias-driver04/reavaliacao-20c7bc4/matriz-qa.py
python -m pytest -q -p testes.integration.conftest ../docs/qualidade/release-2/auditoria-bugs/evidencias/test_qa_aprovacao_permissoes.py
python -m pytest -q -s ../.tmp/qa-release2-08a62f5/test_qa_driver06_http.py ../.tmp/qa-release2-08a62f5/test_qa_driver06_limites.py
python -m pytest -q -s -p testes.integration.conftest ../docs/qualidade/release-2/auditoria-bugs/evidencias/test_qa_aprovacao.py
```

```sh
# A partir de frontend
npm run build
npm run test:e2e:regressao -- --browser chrome
npm run test:e2e:login -- --browser chrome
```

O ensaio adicional no navegador usa o script [qa-sessao.mjs](evidencias/qa-sessao.mjs) com `--medir-driver06`, Chrome descartável, fixture do guia e PostgreSQL exclusivo da auditoria. A observação no Chrome mede da consulta até o corpo completo e até a presença do formulário de login, com relógio monotônico do navegador. A expiração foi induzida no registro de sessão de teste e a invalidação foi feita pelo endpoint de logout. O primeiro ensaio de medição foi descartado porque armava a medição antes de a consulta inicial da tela terminar. A execução registrada aguarda o controle HTTP 200 antes de cada tentativa.

## 4. Cobertura funcional e dos drivers

### Funcional

| Item | Critérios exercitados | Resultado e evidência |
|---|---|---|
| US01–US08 e Driver05, regressão | Login e logout, proteções por perfil, máquinas, produtos, famílias e associação, ordens, prazo e prioridade, bloqueio de tentativas de login | Suítes de backend aprovadas. A reação inicial a identidade indisponível falhou no ensaio exploratório. [Pytest](evidencias/pytest-resumo.json) · [ACHADO-02](bug-restauracao-sessao-indisponivel.md) |
| US09, US10 e US26 | Duração estimada, cadastros e relações, tempos de setup direcionais e associação de produtos a máquinas ativas | Exercitados pela API no Pytest. Cobertura de navegador complementar nos fluxos que consomem esses cadastros. [Pytest](evidencias/pytest-resumo.json) |
| US11 | CT-105 e CT-106, direção da matriz, família ausente e estado vazio | 4 cenários aprovados no Chrome, incluindo os dois retestes da issue #18. [Spec Cypress](../../../../frontend/cypress/e2e/matriz-setup.feature) |
| US12 | Persistência, ordem dos itens, estados vazios e rejeição de entradas inválidas na montagem manual | 17 testes de API aprovados. A geração e a comparação também verificam que o manual permanece preservado. [Pytest](evidencias/pytest-resumo.json) · [US13 Cypress](../../../../frontend/cypress/e2e/sugestao.feature) |
| US13 | CT-107 a CT-112, seleção de ordens, custo direcional, caso de empate, sugestão persistida, ausência de seleção e mesma família | 10 testes de API passaram. O caso com ordem única verificou setup inicial zero. A cobertura inclui direções de setup controladas, preservação das ordens selecionadas e consulta do manual antes e depois. [Pytest](evidencias/pytest-resumo.json) · [Spec Cypress](../../../../frontend/cypress/e2e/sugestao.feature) |
| US14 | CT-113 a CT-115, prazos, prioridades, desempate, risco de atraso e dados obrigatórios | 11 testes de API e 7 unitários passaram. A regra aprovada e registrada no relatório anterior foi usada como oráculo. Há variantes de 5 e 30 min, com prazo e prioridade controlados. [Reavaliação US14](../revisao-us14.md#reavaliação-após-a-decisão-do-po) · [Spec Cypress](../../../../frontend/cypress/e2e/prazos-prioridades.feature) |
| US15 | CT-116 a CT-119, compatibilidade, máquina inativa e ordem sem alternativa | 8 testes de API e 10 unitários passaram, incluindo as duas ordens de seleção que reproduziam o bug histórico. A aprovação posterior de atribuição desatualizada falhou no ensaio integrado. [Pytest](evidencias/pytest-resumo.json) · [Spec Cypress](../../../../frontend/cypress/e2e/compatibilidade.feature) · [ACHADO-01](bug-aprovacao-maquina-inelegivel.md) |
| US16 | CT-120 a CT-122, comparação com os dois registros, sugestão ausente e fontes preservadas | 4 testes de API passaram. O cenário de catálogo com 503 integra a cobertura da interface. [Pytest](evidencias/pytest-resumo.json) · [Spec Cypress](../../../../frontend/cypress/e2e/comparacao.feature) |
| US17 | CT-123 a CT-125, aprovação de origem manual ou sugerida, ausência de plano e disponibilização ao Operador | 7 testes de API passaram, inclusive repetição e concorrência. O cenário adicional com sugestão desatualizada falhou e compromete a disponibilização de um plano executável. [Pytest](evidencias/pytest-resumo.json) · [Spec Cypress](../../../../frontend/cypress/e2e/aprovacao.feature) · [ACHADO-01](bug-aprovacao-maquina-inelegivel.md) |
| US32 | Perfis administrativos, exclusão, desativação e preservação de vínculos | 44 testes de API aprovados. O caso de aprovador preserva o histórico quando a exclusão retorna 409 e permite desativação. [Pytest](evidencias/pytest-resumo.json) · [Correção integrada](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/c06fb94) |

### Drivers

| Driver / caso | Estímulo e medida | Resultado |
|---|---|---|
| Driver01, CT-126 e CT-127 | 10 cadastros e 10 atualizações de ordens. A sessão PostgreSQL foi encerrada depois de DML e antes do commit. Consulta em nova conexão após cada falha. | 20/20 retornaram HTTP 503 com mensagem, sem gravação parcial ou perda de dados previamente confirmados. Em todas as amostras foi observado encerramento de conexão e comparação de estado. [Amostras](evidencias/driver01-rollback.json) |
| Driver01, CT-128 e CT-129 | Três gravações válidas e reenvio após as vinte falhas | 3/3 controles confirmados por API e banco. 20/20 reenvios gravaram com sucesso. Cobertura de registro de andamento segue pendente. [Evidência](evidencias/driver01-rollback.json) · [Relatório anterior](../revisao-driver01.md) |
| Driver02, CT-94, CT-95 e CT-96 | 20 cadastros com 5 reenvios cada, janela de 24 h, nova chave, conteúdo conflitante e reenvios concorrentes | 8 testes oficiais passaram. O caso de volume confirmou 20 operações e 100 reenvios sem duplicação, com preservação do ID. A fronteira usa relógio controlado. [Testes oficiais](../../../../backend/testes/integration/drivers/test_driver02_idempotency_ordens.py) · [Pytest](evidencias/pytest-resumo.json) |
| Driver04, CT-130 e CT-131 | 14 ações como Operador e 14 sem sessão, com dados válidos e comparação das linhas de negócio antes/depois. Incluídas consulta de candidatos e aprovação. | 28/28 recusas, com HTTP 403 ou 401, sem dados protegidos e sem alterações indevidas. O mínimo de 20 combinações foi superado. Replanejamento e eventual perfil Supervisor separado ficaram pendentes. [Matriz](../evidencias-driver04/reavaliacao-20c7bc4/matriz-qa.py) · [Evidência atual](evidencias/pytest-resumo.json) |
| Driver04, CT-132 | Mesmos 14 controles API como Planejador e fluxos de interface representativos | 14/14 controles API passaram. Os fluxos de interface de sugestão, comparação e aprovação estão na suíte de regressão. [Pytest](evidencias/pytest-resumo.json) · [Regressão Chrome](evidencias/cypress-regressao.json) |
| Driver06, CT-133 e CT-134 | Sessão expirada persistida no banco e sessão invalidada pelo logout. 20 amostras HTTP reais e sequenciais por condição em oito rotas. O intervalo conta até a leitura completa do corpo. | 40/40 HTTP 401. Máximos individuais de **25,466 ms** para expirada e **24,743 ms** para invalidada. Em 20 controles extras com sessão desconhecida o máximo foi **25,212 ms**. Uma escrita por condição retornou 401, sem persistência. Todos abaixo de 2 s no marco HTTP local. [Expirada](evidencias/driver06-http-expirada.json) · [Invalidada](evidencias/driver06-http-invalidada.json) · [Desconhecida](evidencias/driver06-http-desconhecida.json) |
| Driver06, CT-133 a CT-137 | Tempo até o login na interface, sessão válida antes da recusa e limite de expiração | Em `GET /api/families`, o máximo até a resposta completa e até o login foi de **12,6 / 13,7 ms** para expirada e **11,1 / 13,4 ms** para invalidada. O ensaio criou uma nova sessão a cada tentativa e verificou o acesso antes de induzir a recusa. Os dois marcos ficaram abaixo de 2 s no loopback. A API com sessão válida retornou 200 nas oito rotas de controle. Com relógio controlado, 1 μs antes do vencimento retornou 200, na fronteira e 1 μs depois retornaram 401. A confirmação formal do marco de 2 s pelo PO segue pendente. [Pytest](evidencias/pytest-resumo.json) |

## 5. Bugs confirmados

| Referência | Severidade e prioridade sugeridas | Confirmação | Impacto |
|---|---|---|---|
| ACHADO-01 / BUG-004 | Alta e Alta | Duas variantes, 2/2, por API integrada e consulta independente ao PostgreSQL. | Na versão auditada, uma nova aprovação gravava e disponibilizava uma atribuição inviável. [Issue #30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) · [Registro original](bug-aprovacao-maquina-inelegivel.md) · [Reteste](reteste-bug004.md) |
| ACHADO-02 / BUG-005 | Média e Média | Três tentativas, 3/3, no Chrome com sessão real e 503 inicial simulado. | Na versão auditada, o Planejador perdia a navegação e precisava recarregar para recuperar a sessão. [Issue #31](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31) · [Registro original](bug-restauracao-sessao-indisponivel.md) · [Reteste](reteste-bug005.md) |

## 6. Suspeitas, lacunas e riscos operacionais

- O downgrade da US14 segue como risco histórico registrado no PR #23. A revisão original reproduziu falha ao recriar a restrição antiga com uma sugestão válida de setup 30/5 já gravada. O upgrade da versão atual passou. O downgrade com dados foi deixado para o ensaio do procedimento de reversão da release. [Revisão US14](../revisao-us14.md#downgrade-falha-após-gravar-sugestão-válida-com-aumento-de-setup) · [PR #23](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/23)
- Na auditoria original, o ACHADO-01 demonstrou uma nova aprovação após a mudança de elegibilidade. O reteste posterior também confirmou a recusa quando a transação de cadastro estava em andamento. A política operacional para planos **já aprovados** continua fora do escopo dessa correção. [Reteste](reteste-bug004.md)
- O catálogo público consultado não contém registro de homologação da R2, e a versão implantada segue não verificada. O checkout integrado e a execução local estão identificados pelo SHA. [Inventário de integração](evidencias/github-integracao.json)

## 7. Reteste dos três bugs históricos

| Registro | Correção integrada | Resultado no SHA auditado |
|---|---|---|
| [#18 / BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18), US11 | [PR #21](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/21), merge `8f992a1`. A matriz incorpora os códigos de origem e destino ausentes da lista de famílias. | **2/2 retestes no Chrome**, CT-105 e CT-106. O ensaio da tela injeta a inconsistência da consulta e verifica os eixos, 15 min, direção inversa e contador. [Cenários](../../../../frontend/cypress/e2e/matriz-setup.feature#L22-L39) |
| [#19 / BUG002](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19), Driver06 | [PR #17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/17), correção `c172886`, merge `a118dcd`. A resposta 401 do recurso remove a área autenticada. | **2/2**, em Famílias e Máquinas, com respostas simuladas no Chrome. O ACHADO-02 tem como gatilho o 503 inicial com uma sessão que continua válida. [Cenários](../../../../frontend/cypress/e2e/autenticacao/driver06.feature#L26-L39) |
| [#25 / BUG-003](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/25), US15 | [PR #24](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24), correção `ae8ae27`, merge `db73ab8`. A geração encontra distribuição viável quando faltam setups na primeira atribuição. | Passou no backend para os dois sentidos de seleção. O cenário `US15_CT05` também passou no Chrome e verificou as duas máquinas, setup total zero e os dois itens gravados. [API](../../../../backend/testes/integration/test_us15_compatibilidade.py#L123-L144) · [Cypress](../../../../frontend/cypress/e2e/compatibilidade.feature#L47-L55) |

As três issues permanecem fechadas. A busca pública por registros equivalentes retornou essas três issues. O backlog do Jira ficou fora do acesso da auditoria. [Registros consultados](evidencias/github-integracao.json)

## 8. Causa provável, correção e regressão após o ajuste

- **ACHADO-01.** A geração verifica a compatibilidade atual e descarta máquinas inativas. Na aprovação, a lista de candidatos filtra ordens pendentes e ainda livres. O POST verifica origem, ordem e conflito com outra aprovação, depois copia a máquina da sugestão para a aprovação. A reprodução confirma que basta alterar o cadastro após a geração para chegar ao `201`. Validar elegibilidade atual no POST, na mesma transação usada para criar a aprovação, e sinalizar a sugestão indisponível na listagem de candidatos. Preservar a fonte histórica e a repetição idempotente de aprovações já existentes. O teste de regressão deve fazer a nova aprovação recusar as duas variantes, manter vazias as tabelas de aprovação e impedir sua exibição ao Operador. Retestar aprovação manual, sugestão elegível, conflitos de concorrência e catálogo atualizado. [Geração](../../../../backend/app/api/routes/sugestoes_planejamento.py#L91-L120) · [Aprovação na versão auditada](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f/backend/app/api/routes/aprovacoes_planejamento.py#L124-L166)
- **ACHADO-02.** `buscarUsuarioAutenticado` distingue 401 de outros erros, mas `restaurarSessao` termina no estado de login ao capturar qualquer falha. A sincronização periódica só existe enquanto há usuário no estado da aplicação. Acrescentar um estado recuperável para falha temporária de identidade e uma ação explícita de nova consulta, com mensagem própria. Manter bloqueada a área protegida até obter identidade válida. O teste de regressão deve falhar se um 503 inicial mostrar diretamente o formulário sem opção de recuperar a sessão, e passar quando a nova consulta 200 restaurar a navegação. Retestar também o 401 inicial, expiração com navegação aberta, logout e os dois cenários da issue #19. [Restauração na versão auditada](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f/frontend/src/App.tsx#L33-L85) · [Reação ao 401](../../../../frontend/src/lib/apiFetch.ts#L1-L12)

## 9. Limitações e ações para o fechamento

| Item | Situação |
|---|---|
| Qualidade da release | Q-01 e Q-02 precisam do inventário completo dos casos do plano, incluindo os manuais. A amostra de CI valida o SHA e não mede a estabilidade histórica de Q-06. Q-07 exige p95 das operações principais em condições de carga próprias, diferente da medição de recusas do Driver06. O ACHADO-02 é uma falha observada no tratamento de erros de Q-09. |
| Severidade e triagem | O plano Q-03 exige zero bugs altos ou críticos em aberto no fechamento. Existe um defeito alto confirmado nesta auditoria. O contador oficial do Jira permanece sem verificação. |
| DoD da integração e da entrega | A regressão e a CI foram verificadas no código integrado. A consulta à época encontrou revisões de aprovação nos PRs #22, #27 e #28 do subconjunto auditado. A DoD das entregas integradas e o aceite do PO constam do registro de entregas. [Inventário GitHub](evidencias/github-integracao.json) · [DoD das entregas](../../../status-projeto.md#definition-of-done-dod) |
| Homologação e fluxos pendentes | Executar smoke com a versão publicada, validar o procedimento de reversão em banco isolado e completar Driver01/04 quando o andamento e o replanejamento estiverem disponíveis. Confirmar com o PO o marco de medição do Driver06. |

## 10. Parecer da auditoria original

**Pendente de ajustes em `08a62f5d` na data da auditoria.** O parecer recomendou corrigir a aprovação com máquina inelegível e a recuperação da identidade e retestar a expiração de sessão. Os resultados dos retestes estão nas seções seguintes.

## 11. Reteste do BUG-004

Em 26/11/2026, a correção do [BUG-004](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) foi validada localmente nas duas variantes. A API recusou a aprovação com HTTP 409, preservou a sugestão para consulta e manteve vazia a execução do Operador. A regressão final passou com 331 testes de backend e 12 cenários no Chrome. O parecer se aplica ao código de [`b6c72f2`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/b6c72f2beb9c4ba92a4c7871547c895574c8afd2), com integração à `main` pendente. [Relatório e evidências](reteste-bug004.md)

## 12. Reteste do BUG-005

Em 26/11/2026, a correção do [BUG-005](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31) foi validada localmente. Após uma falha temporária de identidade, o botão **Tentar novamente** restaurou o painel quando a API respondeu 200 com a sessão válida. Uma resposta 401 real abriu o login, e uma resposta 200 atrasada após a rejeição de um recurso protegido foi descartada. O parecer se aplica ao código de [`8978fc1`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/8978fc110480f363b65873443c072bcc4469cfd6), com integração à `main` pendente. [Relatório e evidências](reteste-bug005.md)
