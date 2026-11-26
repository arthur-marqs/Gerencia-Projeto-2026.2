# Revisão de QA — Driver01 | Integridade dos dados

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Item | `feat(driver01): tratar falhas de persistência em ordens` |
| Release / Sprint | Release 2 / Sprint 3 |
| Repositório | [arthur-marqs/Gerencia-Projeto-2026.2](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2) |
| Issue | Sem vínculo no PR. A busca no repositório por `driver01` e por `persistência` + `ordens` não localizou uma issue correspondente. A definição usada é a fornecida na solicitação. |
| PR / branch | [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26), `feature/driver01-integridade-dados` → `main`. Aberto, sem merge e sem revisão submetida na data da consulta. |
| Commit avaliado localmente | [`70ea1d43f19f43bdf0b8b0d832f4488c92a62814`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/70ea1d43f19f43bdf0b8b0d832f4488c92a62814), igual ao head do PR. |
| Commit testado pela CI do PR | Merge temporário `4dd77e009efe118d6c237bbe0fe6376a2cf92bfa` de `70ea1d4` com `main` em `db73ab8`. [Execução CI nº 171](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45723576956) |
| Data e ambiente | 25/11/2026 (America/Sao_Paulo). Windows, Python 3.11.9, pytest 8.4.2, FastAPI 0.162.0, SQLAlchemy 2.1.6, psycopg 3.3.6 e PostgreSQL 18.6. Bancos descartáveis `qa_driver01_test` e `qa_driver01_http_test`, em `127.0.0.1:55441`, com dados sintéticos. |

As referências de aceite são o estímulo, a resposta, a meta e a DoD da solicitação. O anexo `Plano-de-Teste-SetupFlow-3.md` registra a revisão **2.4 de 23/11/2026** no histórico e ainda exibe **2.3 / Sprint 2** na identificação. Foi adotada a seção da Sprint 3 que define CT-126 a CT-129. O repositório foi confirmado pelo `origin` e pelo PR, pois o plano exibe outro endereço. Também foram consultados os guias do projeto, o template de PR, a arquitetura, o modelo de dados e o workflow. A busca local e na árvore versionada não encontrou `AGENTS.md`. [Guia dos testes](../../../backend/README.md#testes-de-integração-da-us01) · [Arquitetura](../../arquitetura/arquitetura.md) · [Modelo de dados](../../arquitetura/modelo-de-dados.md)

## 2. Parecer resumido e principais pendências

**Pendente de ajustes.** Na API local, **20/20 falhas reais de conexão** antes do `COMMIT` retornaram `503` com mensagem de falha, preservaram o estado persistido e permitiram o reenvio com sucesso. Foram **10 cadastros** e **10 atualizações de campos da ordem**, com **zero gravações parciais**. Os três controles positivos (cadastro, duração e prazo/prioridade) foram confirmados por nova requisição e por consulta independente ao banco. [Evidência por tentativa](evidencias-driver01/desconexao-http.jsonl)

A atualização do **andamento da execução da produção**, prevista no estímulo, está indisponível no incremento, conforme a consulta à API e ao esquema migrado do banco. As edições de duração estimada, prazo e prioridade cobrem alterações de planejamento. A métrica observada foi atingida nessas operações disponíveis e o driver integral permanece **Não verificado**. O guia do backend foi atualizado localmente com o escopo, as respostas e os testes do driver. A inclusão da documentação na versão candidata, a integração do PR, a aplicabilidade da homologação e o aceite do PO permanecem pendentes. [Inventário da API e do banco](evidencias-driver01/andamento-disponibilidade.json) · [Guia do backend](../../../backend/README.md#integridade-da-gravação-de-ordens-driver01)

## 3. Rastreabilidade

O estímulo avaliado é a perda temporária da comunicação com o PostgreSQL durante uma escrita, com dados anteriores confirmados. Espera-se interromper a operação, desfazer as alterações sem confirmação, informar a falha e preservar os dados anteriores. A unidade da medida é uma tentativa de gravação com falha controlada. A meta é 100% em pelo menos 20 tentativas, distribuídas pelo plano em pelo menos 10 cadastros e 10 atualizações. Os sufixos abaixo seguem a convenção de variantes do plano. Os nomes automatizados do PR estão no JUnit.

| Critério/meta | Caso de teste | Evidência | Resultado |
| --- | --- | --- | --- |
| Cenário 1, cadastro após escrita da chave de idempotência | CT-126-01 a CT-126-05. `POST`, desconexão após `INSERT` da operação. | [Rota, `flush`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/app/api/routes/ordens_producao.py#L173-L204) · [Teste do PR, `flush`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/testes/integration/drivers/test_driver01_integridade_ordens.py#L106-L140) · [JSONL](evidencias-driver01/desconexao-http.jsonl) | **5/5**, HTTP 503. Zero ordens novas e zero chaves residuais após a falha. |
| Cenário 1, cadastro após escrita da ordem | CT-126-06 a CT-126-10. `POST`, desconexão depois de gravar a ordem na mesma transação da chave. | [Rota, `commit`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/app/api/routes/ordens_producao.py#L206-L228) · [Teste do PR, `commit`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/testes/integration/drivers/test_driver01_integridade_ordens.py#L143-L176) · [JSONL](evidencias-driver01/desconexao-http.jsonl) | **5/5**, HTTP 503. Zero ordens novas e zero chaves residuais após a falha. |
| Cenário 1, atualização da duração estimada | CT-127-01 a CT-127-05. `PATCH /{id}/duracao-estimada`, desconexão após `UPDATE`. | [Rota](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/app/api/routes/ordens_producao.py#L232-L264) · [Teste do PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/testes/integration/drivers/test_driver01_integridade_ordens.py#L179-L207) · [JSONL](evidencias-driver01/desconexao-http.jsonl) | **5/5**, HTTP 503 e duração anterior preservada. |
| Cenário 1, atualização de prazo e prioridade | CT-127-06 a CT-127-10. `PUT /{id}`, desconexão após o `UPDATE` dos dois campos. | [Rota](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/app/api/routes/ordens_producao.py#L267-L289) · [Teste do PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/testes/integration/drivers/test_driver01_integridade_ordens.py#L210-L249) · [JSONL](evidencias-driver01/desconexao-http.jsonl) | **5/5**, HTTP 503 e ambos os valores anteriores preservados. |
| Cenário 2, sucesso após persistência | CT-128. Executar `POST`, `PATCH` e `PUT` com o banco disponível. Consultar por `GET /{id}` e conexão SQL independente após cada resposta. | [Controle positivo no JSONL](evidencias-driver01/desconexao-http.jsonl) · [Regressão US07–US09 no JUnit](evidencias-driver01/pytest-backend.xml) | **3/3 na API**, HTTP 201/200/200 e valores retornados coerentes com o banco. |
| Recuperação | CT-129. Reenviar a gravação após a desconexão e consultar novamente. Cadastro reusa a mesma chave. | [Campos de recuperação por tentativa](evidencias-driver01/desconexao-http.jsonl) | **20/20 reenvios** na API, com ordem e chave vinculadas nos cadastros. |
| Cenários 1 e 2, mensagens na tela | Ensaio complementar de QA. Cadastro, duração e prazo/prioridade, com `503` seguido de `201/200` simulados. | [Spec Cypress](evidencias-driver01/qa_interface.cy.js) · [JUnit da interface](evidencias-driver01/cypress-interface.xml) | **3/3 no Chrome**. Mensagem de erro no `503`, ausência de sucesso e confirmação após a resposta positiva. |
| Atualização do andamento da execução | CT-127, CT-128 e CT-129 na operação de execução prevista no driver. | OpenAPI da aplicação, schemas de entrada e migrations aplicadas. O plano da Sprint 3 orienta manter a cobertura pendente enquanto a operação estiver indisponível. [Inventário da API e do banco](evidencias-driver01/andamento-disponibilidade.json) · [Modelo de dados](../../arquitetura/modelo-de-dados.md#6-evolução--execução-e-indicadores) | **Não verificado**. A sondagem confirmou que a operação está indisponível. |

## 4. Testes executados e resultados

| Nível | Execução | Resultado |
| --- | --- | --- |
| Revisão estática | Inspeção do diff, rotas, dependência de autorização, sessões ORM, esquema, migrations e tela de ordens. As escritas exigem `PLANEJADOR` na API. A rota trata falhas de gravação com tentativa de `rollback` e HTTP 503. Os três fluxos da tela tratam respostas de erro antes do sucesso. | Rastreado nas rotas e em [dependências da API](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/app/api/deps.py#L27-L80) e na [tela de ordens](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/frontend/src/features/ordens/pages/OrdensProducaoPage.tsx). |
| Testes isolados da lógica | Testes unitários de seed e sequenciamento incluídos na suíte completa do backend. | **13 aprovados**, computados no total local de 249 como regressão. [JUnit local](evidencias-driver01/pytest-backend.xml) |
| Integração em processo, falha injetada no ORM | Pytest + FastAPI `TestClient` + PostgreSQL. Os 20 testes do PR usam o SQL real e lançam `OperationalError` por `monkeypatch` de `Session.flush` ou `Session.commit`. A sessão da fixture usa configuração diferente da produção. | **249 aprovados, zero falhas, erros ou saltos** em 157,98 s, incluindo os **20/20 do Driver01**. [JUnit local](evidencias-driver01/pytest-backend.xml) · [Fixture](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/70ea1d43f19f43bdf0b8b0d832f4488c92a62814/backend/testes/integration/conftest.py#L64-L80) |
| Automação de interface com respostas simuladas | Cypress 16.3.0, Chrome 158 headless, Node 26.13.0 e Vite 8.3.5. Ensaio avulso na tela real, com respostas HTTP simuladas pelo Cypress. | **3 aprovados**, verificando os alertas, a ausência de confirmação no erro e o sucesso na nova tentativa. [JUnit da interface](evidencias-driver01/cypress-interface.xml) |
| Integração por HTTP e conexão real | Ensaio avulso de QA com Uvicorn, sessão normal da API, psycopg e PostgreSQL via TCP local. Depois que o PostgreSQL executou a escrita, uma conexão independente chamou `pg_terminate_backend` para fechar somente a sessão da transação em teste antes do `COMMIT`. O driver registrou `OperationalError` e o SQLAlchemy classificou a conexão como interrompida. | **20/20 (100%)**, zero gravações parciais, 20 respostas 503 com mensagem e 20 recuperações. CT-128 e CT-129 são controles e ficam fora do denominador da meta. [Ensaio](evidencias-driver01/qa_desconexao.py) · [JSONL com resultados individuais](evidencias-driver01/desconexao-http.jsonl) |
| CI da versão candidata | Ubuntu, Python 3.11, PostgreSQL 18. O log mostra o checkout do merge temporário do PR e a execução nominal dos 20 casos pelo comando `python -m pytest -v --junitxml=junit.xml testes`. | **269 aprovados na CI**, incluindo **20/20 do Driver01**. Os cinco jobs da execução passaram. O total local de 249 pertence ao head da branch, cuja árvore difere da combinação com `main` da CI. [Job Backend pytest](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45723576956/job/139587663998) · [Workflow](../../../.github/workflows/ci.yml) |

O ensaio HTTP comparou, por nova conexão, todas as linhas de `ordens_producao` e `ordens_producao_operacoes` do banco de teste e o produto associado, antes e depois de cada falha. Também consultou uma ordem previamente confirmada pela API. No reenvio do cadastro, verificou a relação da chave com a ordem e o usuário. Nos reenvios de atualização, verificou os campos alterados por `GET` e SQL.

### Verificação de disponibilidade do registro de andamento

Em 25/11/2026, o PR #26 continuava no head `70ea1d4`. Foi aplicado `alembic upgrade head` no banco exclusivo `qa_driver01_andamento_test`, atingindo a revisão `6b14a2e9c703`. A consulta ao `GET /openapi.json` com `TestClient` na aplicação real retornou `200`. O inventário das rotas de escrita mostrou somente as três gravações de ordens descritas no guia. Os schemas de entrada aceitam dados de cadastro ou alterações em duração, prazo e prioridade. O campo `status` consta na resposta e tem valor inicial `PENDENTE` no banco. [Evidência](evidencias-driver01/andamento-disponibilidade.json) · [Schemas da ordem](../../../backend/app/schemas/ordem_producao.py)

A consulta a `pg_tables` no esquema `public` e a `information_schema.columns` em `ordens_producao` confirmou o esquema migrado. As entidades de execução e pausas permanecem na evolução do modelo. A busca no código dos 19 commits de ponta das referências locais, incluindo `main`, e nas branches e PRs do GitHub por execução também não encontrou um candidato disponível para teste. A sondagem confirma a indisponibilidade. Os testes de gravação, rollback e recuperação do andamento começam quando houver uma operação executável. [Inventário da API e do banco](evidencias-driver01/andamento-disponibilidade.json) · [Modelo previsto](../../arquitetura/modelo-de-dados.md#6-evolução--execução-e-indicadores)

### Reprodução no PowerShell

Na pasta `backend`, com as dependências instaladas e dois bancos descartáveis já criados. Ajuste as URLs para o PostgreSQL de QA. A fixture da suíte limpa tabelas. A conta do ensaio HTTP precisa poder encerrar outra conexão da própria conta no PostgreSQL isolado. O ensaio aplica as migrations, cria os dados sintéticos e inicia e encerra o Uvicorn localmente.

```powershell
$python = '.\.venv\Scripts\python.exe'
New-Item -ItemType Directory -Force ../.tmp/qa-driver01 | Out-Null
$env:TEST_DATABASE_URL = 'postgresql+psycopg://qa_driver01@127.0.0.1:55441/qa_driver01_test'
& $python -X utf8 -m pytest testes -q -ra --junitxml=../.tmp/qa-driver01/pytest-backend.xml

$env:PYTHONPATH = (Get-Location).Path
$env:TEST_DATABASE_URL = 'postgresql+psycopg://qa_driver01@127.0.0.1:55441/qa_driver01_http_test'
& $python -X utf8 ../docs/qualidade/release-2/evidencias-driver01/qa_desconexao.py
```

Na máquina avaliada, o executável do `.venv` apontava para uma instalação indisponível no sandbox. Foi utilizado o Python 3.11.9 instalado no Windows com os pacotes já existentes em `backend/.venv/Lib/site-packages` no `PYTHONPATH`.

Para repetir o ensaio visual, execute `node node_modules/vite/bin/vite.js build --outDir ../.tmp/qa-driver01/interface/dist` na pasta `frontend` e sirva a compilação com `node node_modules/vite/bin/vite.js preview --outDir ../.tmp/qa-driver01/interface/dist --host localhost --port 5181 --strictPort`. Copie `qa_interface.cy.js` para `.tmp/qa-driver01/interface`. Nesse projeto temporário, configure `e2e.baseUrl` como `http://localhost:5181`, `e2e.specPattern` como `qa_interface.cy.js` e `e2e.supportFile` como `false` no `cypress.config.cjs`. A partir de `frontend`, execute `node node_modules/cypress/bin/cypress run --project ../.tmp/qa-driver01/interface --browser chrome --headless`.

## 5. Bugs e pendências

A revisão não reproduziu perda parcial nem confirmação indevida nos fluxos e pontos de falha exercitados. Nenhuma issue duplicada foi encontrada nas buscas descritas na identificação. O vínculo de acompanhamento encontrado é o [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26).

### Atualização do andamento da produção indisponível para validar

- **Classificação e severidade sugerida.** Pendência de aceite e da DoD, alta para o aceite do driver porque falta uma operação explicitamente prevista no estímulo e ela impede comprovar a meta no escopo integral.
- **Comportamento afetado.** Cenários 1 e 2, meta do Driver01 e CT-127 a CT-129. Ordem preparada para execução, com dados já confirmados, e acesso de Operador/Supervisor no ambiente isolado.
- **Passos e resultado observado.** No commit `70ea1d4`, consultar as rotas de escrita com `GET /openapi.json`, aplicar as migrations em um banco descartável e conferir o esquema persistido. As gravações presentes são o cadastro da ordem, a duração estimada e o prazo/prioridade. A gravação do andamento está indisponível. O cenário ficou bloqueado antes da injeção de falha. [Inventário da API e do banco](evidencias-driver01/andamento-disponibilidade.json)
- **Resultado esperado e critério de fechamento.** Dado um registro de andamento previamente confirmado, quando uma nova atualização válida sofrer desconexão após a primeira escrita e antes da confirmação, então o sistema deve informar a falha e uma consulta independente deve encontrar somente o estado anterior, com seus vínculos íntegros. Quando a mesma operação válida for executada com o banco disponível, então deve confirmar o sucesso e tornar o novo estado consultável. Incluir a operação na medição de CT-127 e registrar CT-128/CT-129 aplicáveis.

### Revisão, integração, documentação e aceite ainda pendentes

As evidências abaixo foram consultadas com o PR aberto e no head `70ea1d4`. São pendências da DoD. O impacto é de processo e rastreabilidade, sem severidade funcional atribuída.

| Pendência | Como conferir e o que foi observado | Critério verificável de fechamento |
| --- | --- | --- |
| Revisão e integração via PR | Abrir o PR e conferir Reviews e Merge. O PR está aberto, com revisores solicitados, sem submissão de revisão, e `70ea1d4` está fora de `origin/main` na referência local. [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26) | A entrega tem revisão registrada e integração rastreável em `main`. |
| Inclusão da documentação na versão candidata | O commit `70ea1d4` altera a rota e seu arquivo de teste. O guia atualizado no workspace registra as operações cobertas, a resposta em caso de indisponibilidade e como executar os testes. [Guia do backend](../../../backend/README.md#integridade-da-gravação-de-ordens-driver01) · [Diff do PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26/files) | O guia atualizado consta no diff da versão candidata. |
| Homologação, se exigida | Consultar a configuração da CI e o registro de implantação da release. O workflow observado executa testes, lint e build. A regra de obrigatoriedade e evidência de implantação não foram localizadas. [Workflow](../../../.github/workflows/ci.yml) | A release registra a aplicabilidade. Se exigida, o ambiente e a versão implantada estão identificados e a execução de homologação está vinculada. |
| Aceite do PO | Verificar decisão no PR ou na issue oficial. O PR está sem aceite registrado e sem issue vinculada. [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26) | Existe decisão do PO rastreável à versão candidata e às evidências de aceite. |

## 6. Verificação da DoD

| Critério vigente | Estado | Evidência e justificativa |
| --- | --- | --- |
| Código revisado e integrado via Pull Request | **Não atendido** | PR aberto, sem revisão submetida e sem merge. [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26) |
| Critérios de aceite atendidos e validados pelo QA | **Não atendido** | Evidência positiva nas operações disponíveis. A atualização do andamento prevista no driver permanece **Não verificado** e bloqueia a validação integral. [Ensaio de QA](evidencias-driver01/desconexao-http.jsonl) |
| Testes escritos e passando | **Atendido** | Os 20 casos versionados do Driver01 passaram localmente e no merge temporário do PR. A cobertura em falta consta no critério de aceite acima. [JUnit local](evidencias-driver01/pytest-backend.xml) · [Job da CI](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45723576956/job/139587663998) |
| Pipeline de CI sem falhas | **Atendido** | Cinco jobs aprovados na execução associada ao PR e ao head avaliado. [CI nº 171](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45723576956) |
| Implantado em ambiente de homologação, quando exigido | **Não verificado** | A exigência para esta release e a evidência de implantação aguardam confirmação. |
| Documentação atualizada | **Não atendido no commit avaliado** | O guia foi atualizado no workspace e aguarda inclusão na versão candidata. [Guia do backend](../../../backend/README.md#integridade-da-gravação-de-ordens-driver01) · [Diff do PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26/files) |
| Aceita pelo PO | **Não verificado** | Nenhuma decisão do PO vinculada à versão foi localizada. [PR #26](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26) |

## 7. Reteste e regressão

- **Validação da correção entregue.** CT-126/CT-127 demonstraram o tratamento de falhas no head avaliado. CT-129 verificou a retomada normal após cada falha. Nenhuma correção posterior foi disponibilizada para reteste nesta avaliação.
- **Regressão executada.** Dos 249 testes locais, 229 são externos ao Driver01. Os diretamente afetados são os 9 da US07 (cadastro, consulta, validação e acesso), 7 da US08 (prazo, prioridade, ordem inexistente e perfil), 10 da US09 (duração, validação e perfil) e 8 do Driver02 (reenvio com a mesma chave, conflito, concorrência, rollback e entradas inválidas). A suíte também executou a regressão de autenticação e planejamento, incluindo US12–US14, porque o planejamento consome as ordens e seus campos. [JUnit local](evidencias-driver01/pytest-backend.xml)
- **Regressão da interface.** Três resultados positivos após falhas simuladas confirmaram a retomada do cadastro e das duas edições de ordem no Chrome. [JUnit da interface](evidencias-driver01/cypress-interface.xml)
- **Reteste pendente.** Quando a gravação do andamento existir, executar os cenários negativos e positivos e repetir a medição no candidato integrado à release, mantendo as variantes de cadastro e incluindo a operação de execução nas atualizações. Usar dados confirmados, interromper a sessão após uma escrita e antes do `COMMIT`, conferir todas as tabelas e relações da operação em nova conexão, registrar o HTTP e a mensagem visual e repetir com o banco disponível.

## 8. Limitações da avaliação e ações pendentes

- A medição reproduziu perda de conexão de uma sessão no PostgreSQL local durante escritas, sob execução sequencial. O recorte inclui falhas antes do `COMMIT`. A perda de comunicação no instante do `COMMIT`, quando a confirmação pode se perder após a gravação, ficou fora do ensaio. Caso seja relevante para a release, reproduzir separadamente e consultar a ordem e a chave antes de reenviar.
- A verificação visual usou dados e respostas simulados no Chrome. O ensaio com desconexão real exercitou a API HTTP e o banco. A cadeia completa navegador–API–PostgreSQL durante a falha ficou sem execução.
- A suíte oficial cobre reenvios simultâneos no Driver02. O ensaio de desconexão não combinou essa condição com duas atualizações concorrentes da mesma ordem.
- Falta validar o fluxo do andamento da produção, incluir o guia atualizado na versão candidata e registrar revisão, integração e decisão do PO. Confirmar a exigência de homologação e vincular a execução, se aplicável.

## 9. Parecer final

**Pendente de ajustes.** O incremento preservou a integridade em **20/20 desconexões reais antes do `COMMIT`** nas operações disponíveis. A ausência do registro de andamento impede validar o driver integralmente e a DoD da entrega continua incompleta. O aceite do item cabe ao PO.
