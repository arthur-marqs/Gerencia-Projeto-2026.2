# Revisão de QA — Driver06: expiração e invalidação de sessão

## 1. Identificação

| Campo | Versão avaliada |
| --- | --- |
| Projeto / repositório | SetupFlow — [arthur-marqs/Gerencia-Projeto-2026.2](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2) |
| Item / issue | Driver06 — [SC-61 no Jira](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-61), conforme vínculo do PR.  |
| PR / branch | [PR #17](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/17), aberto — `feature/driver06-expiracao-sessao` → `main` |
| Release / sprint | Release 2 / Sprint 3|
| Commit avaliado localmente | `16abb603959ceaad3852cf52a50c058fbb3f8454` |
| Base informada pelo GitHub | `5cf655eef47a453ca95eaab5818b93d8fc6415d9` |
| Commit da execução de CI consultada | Merge de teste `ae6f77152adf498ac7bad6fd67aef7e1ae437362`, combinando o head acima com a base acima; não é o SHA do head |
| Data da avaliação | 23/11/2026, America/Sao_Paulo. Cypress existente finalizado às 10:27:32; adicional às 10:30:53. |
| Ambiente local | Windows, build 26200; Python 3.11.9; FastAPI 0.162.0; SQLAlchemy 2.1.6; psycopg 3.3.6; pytest 8.4.2; PostgreSQL 18.6; Node 26.13.0; Vite 8.3.5; Cypress 16.3.0; Chrome headless 157.0.8103.79 |
| Isolamento | Instância PostgreSQL temporária em `127.0.0.1:55436`, banco exclusivo `qa_driver06_test`, migrations aplicadas até `f032ad660001`; dados fictícios reinicializados pelas fixtures. API do ensaio HTTP em `127.0.0.1:8006`. Frontend em `localhost:5173`. |

O diretório de trabalho estava limpo antes da avaliação. O diff do PR contém 14 arquivos, 306 inserções e 41 remoções: testes de backend/Cypress e tratamento de sessão no frontend. O backend de autenticação já existia na base. Nenhum arquivo de implementação foi corrigido; os únicos novos arquivos são este relatório e suas evidências. O teste Cypress temporariamente copiado para o frontend foi removido pelo executor.

O [manifesto de evidências](evidencias-driver06/manifesto.json) registra SHA-256 e tamanho dos arquivos preservados, vinculados ao commit avaliado.

Fontes consultadas: [README](../../../README.md), [guia do backend](../../../backend/README.md), [guia Cypress](../../../frontend/cypress/README.md), [modelo de dados](../../arquitetura/modelo-de-dados.md), [template de PR](../../../.github/pull_request_template.md), [workflow](../../../.github/workflows/ci.yml), [Plano de Teste](../Plano-de-Teste-SetupFlow.docx) e [Plano de Qualidade](../Plano-de-Qualidade-SetupFlow.xlsx). Não foi localizado `AGENTS.md` no repositório. Os arquivos DOCX/XLSX foram lidos por extração do XML interno.

## 2. Parecer resumido e principais pendências

**Pendente de ajustes.** A API negou acesso com sessões rejeitadas e cumpriu a meta quantitativa no ambiente local medido. Entretanto, foi reproduzida falha no retorno ao login: se uma funcionalidade responde **401** e a consulta subsequente de identidade responde **503**, a interface conserva a tela autenticada. O mesmo defeito aparece em Famílias e Máquinas e afeta o Cenário 1.

Resultados principais:

- **4/4 testes preexistentes do Driver06 aprovados**; 20/20 tentativas após logout recusadas, máximo de **0,0089 s** com TestClient e PostgreSQL real.
- **197/197 testes restantes do backend aprovados**, incluindo autenticação, autorização, cadastros, ordens, planejamento, usuários e drivers anteriores.
- Ensaio adicional desta revisão com **HTTP real, Uvicorn e PostgreSQL: 60/60 recusas**, sendo 20 após logout, 20 com expiração persistida e 20 com token desconhecido. Maior tempo: **0,024826 s**. Três escritas adicionais recusadas sem persistência.
- **8/8 cenários Cypress existentes aprovados**, com respostas simuladas. No conjunto adicional de QA: **2 aprovados e 2 reprovados**, correspondentes a duas manifestações do mesmo defeito.
- Lint e build aprovados. A CI consultada está verde e seus logs comprovam a execução dos testes do driver, mas isso não elimina o defeito encontrado.
- **DoD vigente: Não verificado.** Não foi localizada a definição formal da Release 2. O checklist do PR e o plano referente à Release 1 não foram promovidos a uma DoD presumida.

## 3. Rastreabilidade

Os nomes abaixo são os nomes reais dos testes/cenários. Os ensaios adicionais estão explicitamente identificados; não foram atribuídos IDs oficiais de casos inexistentes.

| Critério/meta | Caso de teste e vínculo com código | Evidência | Resultado |
| --- | --- | --- | --- |
| Cenário 1: negar sessão invalidada | `test_driver06_sessao_invalidada_rejeita_20_tentativas` e `test_driver06_rota_protegida_com_sessao_valida_e_invalidada`; autenticação em `backend/app/api/deps.py:25`, logout em `backend/app/api/routes/auth.py` | [Log](evidencias-driver06/pytest-driver06.txt), [JUnit](evidencias-driver06/pytest-driver06.xml) | **Aprovado na API**, TestClient + banco real |
| Cenário 1: negar sessão expirada | `test_driver06_rota_protegida_rejeita_sessao_expirada`; filtro `Sessao.expira_em > agora` em `backend/app/api/deps.py:44` | Mesmo JUnit; teste existente avança o relógio da dependência por monkeypatch | **Aprovado** nesse ensaio; relógio simulado, sem espera real pelo TTL |
| Cenário 1: negar estados inválidos em APIs protegidas | Adicional `test_qa_http_20_tentativas_por_estado[invalidada/expirada/desconhecida]`; login/logout reais e expiração alterada no banco isolado | [Teste adicional](evidencias-driver06/test_qa_driver06_http.py), [JUnit HTTP](evidencias-driver06/pytest-http.xml), [amostras invalidada](evidencias-driver06/http-invalidada.json), [expirada](evidencias-driver06/http-expirada.json), [desconhecida](evidencias-driver06/http-desconhecida.json) | **Aprovado** nas 60 requisições medidas e nas 3 escritas adicionais |
| Cenário 1: direcionar para nova autenticação | Cypress `Retornar ao login após a sessão expirar` e `Retornar ao login quando a sessão for invalidada em outra funcionalidade`; `App.tsx:87`, `apiFetch.ts:9`, `FamiliesPage.tsx:98` | [Resumo Cypress existente](evidencias-driver06/existente/resumo.json) | **Aprovado com API simulada** quando tanto o recurso quanto `/auth/me` retornam 401 |
| Cenário 1: solicitar autenticação depois de 401, mesmo com falha posterior em `/me` | Adicionais `deve solicitar autenticação após 401 em Famílias de produtos, mesmo se /me retornar 503` e equivalente em Máquinas | [Resumo adicional](evidencias-driver06/adicional/resumo.json), [captura Famílias](evidencias-driver06/bug-familias.png), [captura Máquinas](evidencias-driver06/bug-maquinas.png) | **Reprovado**, defeito descrito na seção 5 |
| Cenário 2: permitir sessão válida e perfil autorizado | `test_driver06_rota_protegida_com_sessao_valida_e_invalidada`; Cypress `Permitir acesso com sessão válida`; ensaio HTTP confirma 200 nas 8 rotas antes de cada estado inválido | JUnit do driver, resumo Cypress e [teste/log HTTP](evidencias-driver06/pytest-http.txt) | **Aprovado na API**; **aprovado com simulação na interface**. Navegador + API real juntos não executados. |
| Distinguir autenticação de autorização | `test_driver06_sessao_valida_sem_permissao_retorna_403`; adicionais `preserva sessão quando somente a funcionalidade retorna 403/500`; `require_profiles` em `deps.py:58` | JUnit do driver e resumo adicional | **Aprovado** nos casos executados; 403 não encerra sessão |
| Meta: negar 100% de pelo menos 20 acessos com resposta ≤ 2 s | Teste existente de 20 recusas e ensaio HTTP adicional de 20 por estado | Logs e JSONs de amostras acima; detalhamento abaixo | **Atendida para a resposta da API no ambiente local medido**. Resposta completa até a tela de login não foi medida e tem falha funcional conhecida. |

### Condições e medida do driver

- **Estímulo:** tentativa de acessar funcionalidade protegida com sessão/token expirado ou invalidado.
- **Ambiente previsto:** não detalhado na solicitação quanto a carga, infraestrutura, rede ou concorrência; considerado sistema em operação. Não foram criadas exigências adicionais de carga para o aceite.
- **Resposta esperada:** recusa de acesso e solicitação de nova autenticação.
- **Meta mantida:** 100% de pelo menos 20 tentativas negadas, cada resposta em até 2 segundos. A métrica p95 do plano geral não substitui esse limite por tentativa.

| Ensaio | Amostras medidas | Negadas | Máximo | Condição |
| --- | ---: | ---: | ---: | --- |
| Teste preexistente, sessão invalidada | 20 | 20/20 | 0,0089 s / 8,9 ms | FastAPI TestClient em processo + PostgreSQL real |
| HTTP adicional, sessão invalidada por logout | 20 | 20/20 | 0,024826 s / 24,826 ms | Uvicorn + TCP loopback + PostgreSQL real |
| HTTP adicional, sessão expirada no banco | 20 | 20/20 | 0,017751 s / 17,751 ms | Mesmos serviços; `criada_em` e `expira_em` ajustados para o passado, respeitando a constraint |
| HTTP adicional, token desconhecido | 20 | 20/20 | 0,017536 s / 17,536 ms | Mesmos serviços; token sem registro de sessão |

As amostras HTTP são sequenciais, com um cliente, sem carga concorrente, sem proxy, TLS ou rede externa. O intervalo medido inclui envio da requisição e leitura integral do corpo HTTP com `perf_counter`. As 20 tentativas de cada estado alternam entre `/api/families`, `/api/maquinas`, `/api/produtos`, `/api/ordens-producao`, `/api/planejamentos`, `/api/tempos-setup`, `/api/usuarios` e `/api/auth/me`; **não são 20 por rota**. Os JSONs preservam rota, status e duração de cada amostra, sem tokens.

Os testes também verificam acesso válido em todas essas rotas, atribuindo ao usuário fictício os perfis PLANEJADOR e ADMINISTRADOR necessários, e uma tentativa de `POST /api/families` por estado, com confirmação de ausência do registro no banco. A duração dessas três escritas não integra a amostra de 60. A meta está comprovada nesse ambiente para a API; não se extrapola para produção, para todas as operações de escrita ou para o tempo de navegação até o login.

**Resultado obtido:** negação e tempo de resposta da API comprovados; retorno ao login falha no cenário 401 seguido de 503. **Atendeu?** Parcialmente; o item completo não atende ao aceite. **Evidência:** arquivos acima e defeito da seção 5.

## 4. Testes executados e resultados

### Natureza da evidência

| Modalidade | O que foi realizado | Limite da conclusão |
| --- | --- | --- |
| Revisão estática | Diff do PR, autenticação por cookie, persistência da sessão, dependências de autorização, tratamento de 401 e configuração da CI | Leitura não foi contada como teste aprovado |
| Ensaio isolado da lógica | Não foi criado ensaio isolado de autenticação. Os testes unitários já existentes do seed integram a regressão | Não substitui a API |
| Automação com respostas simuladas | Cypress no Chrome: 8 cenários existentes + 4 adicionais de QA | Comprova comportamento do frontend sob as respostas controladas; não comprova integração do navegador com o backend |
| Integração em processo | Pytest/TestClient com migrations e PostgreSQL reais; expiração do teste existente usa monkeypatch de relógio | Não inclui servidor HTTP nem transporte de rede |
| Integração com serviços reais | Ensaio adicional via HTTP para Uvicorn e PostgreSQL reais, sem override de autenticação e sem respostas simuladas | Inclui API e banco; não inclui navegador, proxy ou homologação |

### Comandos reproduzíveis

Na pasta `backend`, usar exclusivamente um PostgreSQL de teste separado. A avaliação utilizou:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://qa_driver06@127.0.0.1:55436/qa_driver06_test'
.venv/Scripts/python.exe -m pytest -v -s --junitxml=../docs/qualidade/release-2/evidencias-driver06/pytest-driver06.xml testes/integration/drivers/test_driver06_session_expiration.py
.venv/Scripts/python.exe -m pytest -v --ignore=testes/integration/drivers/test_driver06_session_expiration.py --junitxml=../docs/qualidade/release-2/evidencias-driver06/pytest-regressao.xml testes
$env:PYTHONPATH = '.'
.venv/Scripts/python.exe -X utf8 -m pytest -v -s --junitxml=../docs/qualidade/release-2/evidencias-driver06/pytest-http.xml ../docs/qualidade/release-2/evidencias-driver06/test_qa_driver06_http.py
```

Resultados: **4 passed in 1.46s**, **197 passed in 43.85s**, **3 passed in 3.81s**, respectivamente. Logs: [driver](evidencias-driver06/pytest-driver06.txt), [regressão](evidencias-driver06/pytest-regressao.txt), [HTTP](evidencias-driver06/pytest-http.txt). Relatórios: [JUnit regressão](evidencias-driver06/pytest-regressao.xml) e os JUnits vinculados anteriormente. O ensaio HTTP inicia e encerra seu próprio Uvicorn; o fixture do projeto aplica as migrations e limpa os dados apenas no banco selecionado.

O [helper temporário de PostgreSQL](evidencias-driver06/qa-postgres.py) documenta a instância descartável utilizada. Depende dos binários PostgreSQL 18 no caminho indicado e de uma pasta temporária ainda inexistente; recusa sobrescrita. Nesta execução, a inicialização do cluster ocorreu no sandbox, mas a partida do servidor precisou ser repetida fora da restrição de processos. A instância foi encerrada ao final; seus dados ficaram na pasta temporária local. Para repetir em outro ambiente, pode-se usar um banco exclusivo já preparado e ajustar a URL, sem depender desse helper.

Na pasta `frontend`, com o servidor Vite em execução:

```powershell
npm.cmd run dev -- --host 127.0.0.1
# Em outro terminal, também em frontend:
node ../docs/qualidade/release-2/evidencias-driver06/qa-cypress.cjs
node ../docs/qualidade/release-2/evidencias-driver06/qa-cypress.cjs --adicional
npm.cmd run lint
npm.cmd run build
```

O [executor de QA](evidencias-driver06/qa-cypress.cjs) usa a configuração existente. No modo adicional, copia [qa-driver06.cy.ts](evidencias-driver06/qa-driver06.cy.ts) para a árvore Cypress, permite specs comuns pelo filtro misto do Cucumber e remove a cópia ao terminar. Essa alteração de configuração só vale para o ensaio; não altera a CI nem as configurações versionadas do produto. O modo adicional retorna código 1 enquanto as duas asserções de retorno ao login falharem.

| Execução frontend | Resultado | Evidência |
| --- | --- | --- |
| Cenários existentes de autenticação | 8 aprovados: 3 do Driver06 e 5 do login | [Log](evidencias-driver06/cypress-existente.txt), [resumo](evidencias-driver06/existente/resumo.json) |
| Casos adicionais de QA | 2 aprovados (403/500 sem logout), 2 reprovados (401 → `/me` 503) | [Log](evidencias-driver06/cypress-adicional.txt), [resumo](evidencias-driver06/adicional/resumo.json), duas capturas |
| Lint | Código de saída 0, sem erros/avisos reportados | [Log](evidencias-driver06/lint.txt) |
| Build | Código de saída 0, TypeScript e Vite concluídos | [Log](evidencias-driver06/build.txt) |

A primeira tentativa de iniciar o Vite falhou com `spawn EPERM` no sandbox; a execução fora da restrição de processos passou sem alteração de código. As primeiras tentativas do ensaio Cypress adicional não encontraram specs devido ao filtro do Cucumber; não foram contadas como execuções de casos. O executor foi ajustado e o resultado conclusivo está no resumo final. A apresentação `NativeCommandError` em logs PowerShell decorre de mensagens INFO do Alembic enviadas ao stderr; os resultados e códigos de saída do Pytest foram 0. Nenhuma dependência foi atualizada.

### CI e vínculo com a versão

A [execução CI #109](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/44908660042), de 21/11/2026, terminou com sucesso nos cinco jobs. Foi consultada pela associação ao head, e os logs de checkout identificam o **merge de teste** `ae6f771...`, combinando `16abb603...` e `5cf655ee...`. A evidência local acima testa diretamente o head.

- [Backend pytest](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/44908660042/job/136859549152): log contém nominalmente os quatro testes do Driver06 aprovados e **201 passed in 48.65s**. O workflow executa `python -m pytest -v --junitxml=junit.xml testes` com PostgreSQL 18. O `-s` não está habilitado nessa execução, portanto o máximo numérico do driver foi obtido localmente, não atribuído ao log da CI.
- [Frontend Cypress BDD](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/44908660042/job/136859548950): embora o YAML mencione `login.feature`, o log informa que o parâmetro `command` faz o action ignorar `spec/config-file/browser`. O script efetivamente usa `cypress.config.ts`, encontra **driver06.feature e login.feature** e aprova **8/8**. Não há pendência de inclusão dos cenários preexistentes do Driver06 na CI.
- Lint/build e US32 BDD em Chrome/Electron têm jobs concluídos com sucesso. Não foram consultados seus casos individuais/artifacts nesta revisão; esses estados não foram contados como nova execução funcional local.

Os [trechos preservados da CI e metadados do PR](evidencias-driver06/github-ci.json) permitem conferir essa associação. Os testes adicionais de QA não fazem parte da CI atual. Nenhum workflow foi disparado ou alterado.

## 5. Bugs e pendências

### Bug — Interface permanece autenticada após 401 se `/auth/me` falhar

| Campo | Registro para abertura pelo QA |
| --- | --- |
| Classificação | **Bug**, reproduzido no frontend real com respostas HTTP simuladas |
| Item / comportamento | SC-61 / Driver06, Cenário 1: direcionar o usuário para nova autenticação após recusa de sessão |
| Severidade sugerida | **Média**: impede o retorno ao login e mantém navegação/formulários autenticados após a recusa. A API continua negando requisições; não foi comprovado acesso indevido a dados protegidos. |
| Localização | [App.tsx](../../../frontend/src/App.tsx), linhas 87–98: o handler de sessão expirada chama uma nova consulta de identidade, e o `catch` conserva o usuário. [apiFetch.ts](../../../frontend/src/lib/apiFetch.ts), linhas 9–10, emite o evento. [FamiliesPage.tsx](../../../frontend/src/features/families/pages/FamiliesPage.tsx), linhas 98–100, chama a mesma revalidação diretamente. |
| Pré-condições | Frontend no commit avaliado; usuário PLANEJADOR inicialmente identificado por `/api/auth/me` 200. O recurso protegido rejeita a sessão com 401; a reconsulta de identidade sofre indisponibilidade 503. |
| Resultado esperado | Solicitar nova autenticação e retirar a tela autenticada após a recusa de sessão. Uma falha posterior na consulta de identidade não deve anular o 401 já recebido. |
| Resultado obtido | Depois de 401 e de confirmação de `/auth/me` 503, o login não aparece durante a espera de 3 s da asserção; menu e página autenticada permanecem. Em Famílias, a tela ainda apresenta formulário e lista vazia. |
| Evidência | [Teste adicional](evidencias-driver06/qa-driver06.cy.ts), [resumo com as duas falhas](evidencias-driver06/adicional/resumo.json), [Famílias](evidencias-driver06/bug-familias.png), [Máquinas](evidencias-driver06/bug-maquinas.png) |
| Limite da confirmação | Reprodução com `cy.intercept`; não foi provocada indisponibilidade real no backend. A duração de 3 s é a janela de observação do teste, não uma nova meta de aceite. O ensaio HTTP separado confirma a proteção da API nas condições medidas. |
| Status / responsável | Identificado nesta revisão; não publicado, sem ID de issue atribuído. Responsável de desenvolvimento a definir pelo time. QA deve acompanhar correção, reteste e vínculo à SC-61. |

Passos reproduzíveis:

1. Interceptar `GET /api/auth/me`: responder 200 com `{ "usuario": { "nome": "QA Driver06", "perfis": ["PLANEJADOR"] } }` na restauração inicial.
2. Interceptar `GET /api/families` para responder 401 com `Sessão inválida ou expirada.` e, a partir dessa resposta, fazer `/api/auth/me` responder 503.
3. Abrir `/`, acessar **Famílias de produtos** e confirmar as respostas 401 e 503, nessa ordem.
4. Verificar que a tela **Acesse sua conta** não aparece e o formulário de família permanece.
5. Repetir em **Máquinas**, usando `/api/maquinas`. O evento compartilhado apresenta o mesmo resultado.

Critério de correção verificável:

```gherkin
Esquema do Cenário: Solicitar autenticação após recusa da sessão
  Dado que o planejador está na interface autenticada
  E que a consulta à funcionalidade protegida responde 401 por sessão inválida
  E que uma consulta posterior à identidade responde 503
  Quando o sistema tratar a recusa da sessão em <funcionalidade>
  Então deve apresentar a tela de login
  E deve remover a navegação e o conteúdo da área autenticada

  Exemplos:
    | funcionalidade       |
    | Famílias de produtos |
    | Máquinas             |
```

No reteste, preservar os controles que passaram: erro 403 ou 500 isolado na funcionalidade, sem 401 de sessão, não deve encerrar a sessão. Ampliar a reprodução para `/me` sem resposta ou com erro de rede; esses dois casos não foram executados e não são bugs adicionais confirmados.

### Pendência da DoD — definição vigente não disponível

- **Afeta:** conclusão da verificação obrigatória da DoD da Release 2 / Sprint 3.
- **Evidência:** o README atribui a conferência da DoD ao PO/QA; o Plano de Qualidade remete a DoD aos acordos da equipe. Nenhum documento consultado enumera a DoD vigente. O Plano de Teste descreve a Release 1; os papéis também diferem do README para a Release 2.
- **Como verificar:** fornecer o acordo vigente e sua versão/data; avaliar cada item contra este commit e anexar o resultado. Critério de encerramento: todos os itens aplicáveis da DoD com status e evidência rastreável.
- **Classificação/impacto:** pendência documental de aceite, sem severidade funcional atribuída. Não comprova defeito no produto e não autoriza presumir a DoD.

### Pendência de rastreabilidade — Jira e planejamento da Sprint 3

- **Afeta:** confirmação da versão vigente da SC-61, plano de testes específico e pesquisa de bugs existentes no Jira.
- **Evidência/limite:** critérios fornecidos na solicitação foram usados integralmente; o PR vincula SC-61, mas a conta Jira não está disponível nos conectores desta avaliação. O plano versionado é referente à Release 1 e não lista o Driver06.
- **Ação de encerramento:** QA conferir no Jira o texto atual, os bugs relacionados e o planejamento da Sprint 3; vincular o caso adicional à SC-61 e ao bug, preservando estes critérios e a meta de 2 s. Não abrir duplicata antes dessa consulta.

**Bugs já registrados:** a pesquisa de issues do GitHub e do PR #17 encontrou [#18](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18), **aberta**, severidade Média declarada, atribuída a `arthur-marqs`, sobre matriz de setup/US11/PR #16. É outro comportamento, fora desta branch, e não deve ser duplicado nem encerrado por este relatório. A discussão e as revisões formais consultadas do PR #17 estavam vazias. Não foi localizado registro equivalente ao defeito de 401/503 no GitHub; a consulta ao Jira continua necessária. Nenhuma issue ou comentário foi publicado.

## 6. Verificação da DoD

**DoD formal vigente: Não verificado.** Sem a definição não é possível enumerar e certificar todos os seus critérios. Não se atribui “Não se aplica” a um requisito desconhecido. A tabela abaixo verifica somente o checklist existente no template do PR, explicitamente como evidência complementar, não como substituto da DoD.

| Critério disponível no checklist de PR | Status | Evidência e fundamento |
| --- | --- | --- |
| Branch atualizada com a base | **Atendido** para a base consultada | Base do PR `5cf655ee...` é ancestral do head; GitHub informa mergeable. Não garante o estado da base após esta avaliação. |
| Código segue o padrão do projeto | **Atendido** no escopo verificável | Lint e build locais aprovados; fluxo de dependências da API revisado. Não há catálogo adicional de padrões localizado. |
| Testes novos/atualizados e todos passando | **Não atendido** | Testes preexistentes passam, mas dois casos adicionais reproduzem o defeito de retorno ao login. |
| Pipeline de CI sem falhas | **Atendido** na execução do PR consultada | CI #109, cinco jobs com sucesso, no merge de teste identificado na seção 4. |
| Critérios de aceite atendidos/validados | **Não atendido** | Cenário 1 falha em 401 → 503, apesar da negação e do tempo da API aprovados. |
| Documentação/README atualizados, se necessário | **Não verificado** | Relatório e evidências agora existem; falta confirmar a documentação/processo exigidos pela DoD e pelo planejamento vigente. Não foi presumida necessidade de alteração de README funcional. |
| Sem segredos/dados sensíveis no código da alteração | **Atendido** no diff revisado | Não foram identificados segredos no diff do PR; dados dos testes são fictícios. Não representa auditoria completa do histórico do repositório. |
| Revisor leu o código e não encontrou problemas | **Não atendido** | Revisão realizada com bug comprovado, seção 5. |
| Revisor executou os passos de “Como testar” | **Atendido** | Driver, autenticação Cypress, lint/build executados localmente; banco isolado e executor equivalente documentados. |
| Sem regressões visíveis | **Não verificado** para todo o frontend | 197 testes restantes e 5 cenários de login passaram; controles 403/500 passaram. Operações completas de todos os módulos na interface não foram executadas. |

Do plano de qualidade disponível, os indicadores **Q-01** (100% dos casos planejados), **Q-02** (≥ 95% de aprovação), **Q-03** (zero bugs críticos/altos), **Q-04** (critérios antes da sprint), **Q-05** (revisão antes de merge), **Q-06** (pipeline da main no fechamento), **Q-07** (p95 das principais operações ≤ 2 s), **Q-08** (autorização por perfis) e **Q-09** (tratamento de erros) foram consultados. Este recorte não comprova as metas de toda a Release 2: não há denominador completo de casos, inventário do Jira ou resultado de fechamento da main. Q-08 tem evidência favorável nas suítes de API; Q-09 tem a falha específica descrita. A medição de recusas do Driver06 não comprova Q-07 para as demais operações. Os critérios de saída do Plano de Teste exigem resultados registrados e evidências; isso foi produzido para este item, mas a completude da sprint e a ausência de bugs críticos/altos no Jira seguem não verificadas.

## 7. Reteste e regressão

**Reteste:** nenhuma correção foi aplicada nesta etapa. Portanto, o defeito permanece sem reteste de correção. Quando houver novo commit:

1. Registrar SHA, diff e vínculo ao bug/SC-61; repetir os dois casos de 401 seguido de `/me` 503 até que ambos passem.
2. Repetir com falha de rede e ausência de resposta em `/me`, comprovando que a recusa anterior ainda leva ao login. Registrar duração sem esperas fixas e confirmar que respostas tardias não restauram a área autenticada.
3. Repetir pelo menos uma expiração e uma invalidação por logout com navegador, API e banco reais; confirmar login, acesso permitido, expiração/invalidação, recusa e nova autenticação. Esse fluxo completo não foi executado nesta revisão.
4. Reexecutar a medição de pelo menos 20 recusas com cada amostra ≤ 2 s e guardar status/duração/ambiente. O roteiro adicional preservado já cobre os três estados e evita uso do banco de desenvolvimento.

**Regressão executada:** 197 testes restantes do backend, além dos quatro do driver, com PostgreSQL real; cinco cenários de login no Chrome com simulações; controles de 403 e 500 sem logout. Inclui comportamentos da Release 1 (US01–US08), US09/US10/US12/US26, gerenciamento de usuários US32 e drivers 02/05, conforme nomes no [log de regressão](evidencias-driver06/pytest-regressao.txt). A suíte de US32 verifica invalidação após desativação, reativação/troca de senha e exclusão, e disputas de transações já existentes. Isso não equivale a testar todas as possíveis corridas de expiração/logout.

**Justificativa do escopo:** o tratamento compartilhado foi aplicado a máquinas, produtos, compatibilidade, ordens, planejamento, tempos de setup e usuários; Famílias usa callback próprio. Uma alteração em `App.tsx` pode afetar login, restauração, sincronização e logout em todos esses módulos. A suíte de backend preserva permissões e persistência; a regressão de frontend ainda precisa cobrir consultas e escritas nesses módulos, logout/relogin, mudança de perfil, foco/visibilidade, múltiplas abas e requisições simultâneas.

**Não executado:** regressão integrada completa desses módulos no navegador; fronteira exata `expira_em == agora` (o código usa `>`); expiração por espera real de oito horas; carga concorrente específica de sessão; rede/proxy/homologação; navegadores além do Chrome local. O Electron da US32 está verde na CI, mas os testes adicionais desta revisão não foram executados nele. Não foi presumida falha funcional para os cenários não executados.

## 8. Limitações da avaliação e ações pendentes

| Limitação / pendência | Ação objetiva do QA/time |
| --- | --- |
| Bug reproduzido em 401 → 503 | Registrar ou vincular no rastreador após checar duplicatas no Jira; desenvolvimento corrigir; QA retestar no novo SHA. |
| DoD vigente indisponível | PO/time fornecer versão dos acordos; QA preencher avaliação de cada critério com evidências. |
| SC-61 e plano da Sprint 3 não consultados no Jira | Conferir versão atual e correspondência com os critérios fornecidos; confirmar bugs/pendências existentes e completar rastreabilidade. |
| Frontend e serviços foram validados separadamente | Executar o roteiro de navegador + API + banco reais do reteste, incluindo login após recusa. |
| Meta medida somente em ambiente local | Se o aceite exigir ambiente específico, repetir ali com pelo menos 20 amostras e registrar todos os tempos; não usar pipeline verde ou p95 para substituir a meta por tentativa. |
| Casos adicionais fora da suíte do produto | Desenvolvimento/QA decidir incorporação permanente dos casos de 401 seguido de falha de identidade e das medições úteis, sem confundi-los com os casos preexistentes. |
| Resultado de CI é de merge de teste | Revalidar CI do próximo head/merge de teste e preservar seu SHA; este parecer vale somente para o head identificado. |

Os scripts adicionais são instrumentos desta revisão, preservados para reprodução. A instância de QA e o Vite iniciados para a avaliação foram encerrados. Credenciais da configuração local existente não autenticaram no PostgreSQL instalado; por isso foi usada a instância temporária, sem modificar o `.env` ou o banco de desenvolvimento. Não houve correção de implementação, mudança de requisito, publicação externa, abertura/fechamento de issue, aprovação ou merge.

## 9. Parecer final

**Pendente de ajustes.** O bloqueio da API e a meta quantitativa foram comprovados no ambiente local descrito, mas o retorno à nova autenticação falha no cenário reproduzido. A DoD vigente também permanece sem comprovação. O item não está apto para aceite neste commit. O parecer de QA não substitui o aceite do PO.