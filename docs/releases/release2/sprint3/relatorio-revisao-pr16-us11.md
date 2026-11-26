# Relatório de revisão e validação — US11: Visualizar matriz de setup

**Situação da entrega em 26/11/2026 · Aprovada pelo PO e integrada à `main`.** [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) (`8d654d3`) e [PR #21](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/21) (`8f992a1`). Os sete critérios do DoD estão concluídos para o incremento aceito. [Definition of Done](../../../status-projeto.md#definition-of-done-dod)

O BUG-001 foi retestado nas duas variantes na versão integrada. As rodadas abaixo registram as evidências e os pareceres de 22 e 23/11/2026. [Reteste na main](../../../qualidade/release-2/auditoria-bugs/relatorio-validacao.md#7-reteste-dos-três-bugs-históricos)

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável pelo QA | @leonardo-istamilo |
| Data da revisão | 23/11/2026 (registros anteriores de 22/11/2026 preservados) |
| História de usuário | SC-28 / US11 — Visualizar matriz de setup |
| Pull Request | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) |
| Branch | `feature/US11-matriz-setup` |
| Commit avaliado | `5abd06aa481e55828e8ce41680ea38aad5c3bc65`; anterior: `4a50a6a7d29cb1f31d73d9983ff5f6b4f0fb88b4`; inicial: `8de6f4adedc15782694c679d9643c20ef83b3993` |
| Ambiente | Local, Windows 10.0.26200, Chrome 157.0.8103.79 headless, Cypress 16.3.0, Python 3.11.9, Node 26.13.0, npm 11.20.0, PostgreSQL 18.6 exclusivo de QA; detalhes em 6.2 |
| Parecer de QA em 23/11/2026 | **Pendente de ajustes — conclusão da DoD**. BUG-001 resolvido e verificado; limitações essenciais de evidência descritas em 8.2. |

**Leitura do histórico:** os resultados de 22/11/2026 foram mantidos nas subseções históricas. As subseções da reavaliação registram a situação observada em **23/11/2026, commit `5abd06a`**, antes da integração. Os rótulos `CT-US11-01` a `CT-US11-04` são aliases históricos deste relatório, não IDs oficiais do plano.

## 1. Objetivo e escopo

Verificar a matriz de setup, os dois cenários de aceite e a Definition of Done da US11. A revisão abrangeu o acesso pelo perfil `PLANEJADOR`, os tempos direcionais entre famílias e o estado sem configurações.

**Dependência:** APIs de famílias e tempos de setup já disponíveis. **Drivers relacionados:** nenhum identificado no escopo da avaliação.

**Limitações da rodada de 22/11/2026:** o reteste do BUG-001 simulou a sessão e as APIs. Os dois cenários nominais foram executados com o backend na CI.

**Escopo da reavaliação:** comparar `4a50a6a..5abd06a`, retestar as duas variantes do BUG-001, repetir os dois cenários nominais, conferir acesso e estados da matriz e executar regressão das dependências e da preparação de dados compartilhada. Não há driver específico vinculado à US11 nos materiais acessíveis. Tempos das suítes são durações de execução, não medições de desempenho ou comprovação de p95.

**Fontes e instruções:** lidos README raiz, guias do backend, frontend e Cypress, templates de PR/US, workflow, relatório integral, evidências anteriores, plano de testes DOCX, plano de qualidade XLSX, feature e steps da US11 e testes das US02/US05/US10. Não foi encontrado `AGENTS.md` na árvore nem nos diretórios ancestrais consultados. O plano DOCX disponível cobre a Release 1 e lista CT-01 a CT-18, sem casos da US11. A planilha de qualidade remete critérios ao backlog e DoD aos acordos da equipe; não contém a definição integral vigente da SC-28. Não há cópia da SC-28 no repositório, URL específica do Jira nos materiais consultados ou conector Jira disponível. A busca `US11` nas issues do repositório retornou apenas o BUG-001. Portanto, a definição vigente e a DoD específica não puderam ser reconfirmadas na fonte oficial; a avaliação funcional usa os dois critérios preservados neste relatório, o PR e os critérios de correção da issue #18, sem presumir requisitos adicionais.

Referências locais: [Plano de testes, versão 1.1 de 29/10/2026](../../../qualidade/Plano-de-Teste-SetupFlow.docx), seções 2.2, 7 e 8; [Plano de qualidade](../../../qualidade/Plano-de-Qualidade-SetupFlow.xlsx), vínculo com DoD/backlog e métricas Q-07 e de homologação. Nenhuma dessas fontes foi alterada.

**Identificação da versão:** `git branch --show-current`, `git rev-parse HEAD`, `git status --porcelain=v1 --untracked-files=all`, `git log` e `git diff 4a50a6a..HEAD` confirmaram a branch solicitada e árvore limpa antes das verificações. O PR #16 consultado está aberto, `merged=false`, com head exatamente `5abd06a` e base `main` em `5cf655e`; não foi avaliado o código da `main`. Não havia trabalho local não commitado a incluir. As mudanças desta tarefa são documentação/evidências de QA e ensaios temporários em `.tmp`, sem edição de produção, requisitos ou testes oficiais. [Snapshot GitHub/CI](evidencias/us11/reavaliacao-5abd06a/github-ci.json) · [Ambiente](evidencias/us11/reavaliacao-5abd06a/ambiente.json).

## 2. Revisão da implementação

### 2.1. Registro histórico — 22/11/2026

| Aspecto | Situação | Observações / evidências |
|---|---|---|
| Comportamento previsto na US | Não conforme | A matriz pode contar uma transição e omitir seu tempo. [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) |
| Regras de negócio | Conforme no fluxo nominal | Linhas são origens, colunas são destinos e os tempos aparecem em minutos. |
| Permissões de acesso | Conforme por revisão de código | Menu, página e endpoints exigem `PLANEJADOR`. A execução utilizou uma sessão simulada desse perfil. |
| Validações e tratamento de erros | Não verificado em execução | O código prevê mensagem de erro e nova tentativa. |
| Estados da interface | Parcialmente verificado | O estado vazio oferece **Atualizar matriz**. A CI validou a atualização mantendo a mensagem de ausência. Carregamento e erro foram revisados por inspeção. |
| Testes automatizados relacionados | Parcialmente atendido | Os dois cenários da US11 passaram no Cypress/Cucumber. Falta cobrir o BUG-001. |
| Documentação exigida | Conforme | O commit documentou a matriz e os cenários de teste nos READMEs do frontend e do Cypress. |

O PR está aberto e o GitHub o indica como mesclável com `main`. Lint e build passaram localmente. [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16)

### 2.2. Reavaliação — 23/11/2026, `5abd06a`

O diff desde `4a50a6a` contém a atualização histórica do relatório (`4471b73`), a união de famílias e novos cenários (`47c63d6`), o ajuste dos seletores (`927efe9`), a aplicação da mesma coleção às colunas (`bbf29c4`) e uma mensagem de diagnóstico em teste do Driver02 (`5abd06a`). A alteração do Driver02 preserva as condições das asserções e não foi tratada como validação desse driver, fora do escopo desta revisão.

| Aspecto | Situação atual | Evidência |
|---|---|---|
| Eixos e transições do BUG-001 | Correção identificada no código **e validada por execução** | `frontend/src/features/matriz-setup/pages/MatrizSetupPage.tsx:134–151` une famílias por ID, incluindo origem/destino dos setups; linhas 235, 251 e 261 usam essa coleção nos três eixos/iterações. Dois retestes oficiais e INV-02/03 passaram. |
| Direcionalidade, minutos, ausência e contador | Conforme nos dados exercitados | Cenário `@matriz-configurada` integrado; INV-01 verifica textos exatos, A → B = 15, B → A = 30, diagonais e contador; INV-02/03 conferem inversa `—` e singular `1 configuração`. |
| Acesso por perfil | Verificado por camadas | Sessão/login real nos quatro cenários oficiais; 4 testes da US02 e bloqueios de consulta na US10; INV-07 verifica menu ausente com sessão de operador simulada. Inspeção: `Sidebar.tsx:20,54,95`, `AuthenticatedPage.tsx:39,68`, rotas `families.py:17` e `tempos_setup.py:21`. |
| Vazio, atualização, carregamento e erro | Verificados, com distinção do ambiente | `@matriz-vazia` usa API/banco reais e repete consulta vazia; INV-04/05/06 usam mocks para atraso, HTTP 500 com recuperação e passagem de vazio para preenchido. Não se afirma falha real de backend nesses ensaios. |
| Testes do BUG-001 na regressão/CI | Resolvido e verificado | Feature: linhas 22–39, tags `@bug001-destino-ausente` e `@bug001-origem-ausente`, herdando `@regressao`; execução local 4/4 e JUnit dos jobs remotos 4/4 em cada navegador. |
| Documentação | Parcialmente atualizada | Funcionalidade documentada em `frontend/README.MD:10–14`; guia Cypress não descreve a natureza simulada dos novos retestes. DOC-US11-01 em 4.3. |

**Qualidade das asserções:** os steps oficiais (`frontend/cypress/support/step_definitions/matriz-setup.js:68–73,140–161`) verificam a célula dirigida, valor por `contain.text`, existência das células cruzadas, inversa e contador. O step dos “dois eixos” infere os eixos pela existência das células, sem conferir diretamente códigos/nomes dos cabeçalhos. Os ensaios temporários INV-01/02/03 complementam essa lacuna com leitura explícita de `thead th` e `tbody tr > th`, nomes/códigos e `have.text`. A melhoria permanente dessas asserções é uma **proposta**, não um caso existente no plano nem uma alteração realizada nesta tarefa.

## 3. Validação dos critérios de aceite

### 3.1. Registros históricos — 22/11/2026

Os identificadores abaixo são locais a este relatório. Os IDs oficiais do plano de testes não foram confirmados.

| Critério / cenário | Caso de teste | Execução | Resultado | Evidência / bug |
|---|---|---|---|---|
| 1. Exibir famílias e tempos cadastrados | CT-US11-01 | Automatizada no Chrome, APIs simuladas | Aprovado no fluxo nominal | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 2. Informar que não há configurações | CT-US11-02 | Automatizada no Chrome, APIs simuladas | Aprovado | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 1. Exibir uma transição cuja família de destino está ausente da lista de famílias | CT-US11-03 | Automatizada no Chrome, APIs simuladas | Reprovado | [Captura](../sprint2/evidencias/us11/ct03-matriz-setup-chrome.png) · [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) |

Os passos abaixo preservam a rodada inicial. A execução mais recente, em `4a50a6a`, está na seção de reteste e regressão.

#### 3.1.1. Registro de execução inicial

**Data / responsável:** 22/11/2026 · QA da US11. **Commit:** `8de6f4a`.

Em cada caso, a execução configurou os retornos simulados de sessão, famílias e tempos, abriu **Matriz de setup** pelo menu lateral e verificou os eixos, as células, o contador ou a mensagem de estado vazio.

| Caso | Pré-condições e dados | Resultado esperado | Resultado obtido |
|---|---|---|---|
| CT-US11-01 | Sessão de planejador, famílias A e B, A → B = 15 min e B → A = 30 min | Ambas as famílias nos eixos, valores nas direções corretas e duas configurações | Os valores, os eixos e o contador conferiram. |
| CT-US11-02 | Sessão de planejador, famílias A e B, lista de setups vazia | Mensagem de ausência de configurações | A tela exibiu **“Nenhuma configuração de setup cadastrada”**. |
| CT-US11-03 | Sessão de planejador, lista de famílias contendo apenas A, setup A → B = 15 min | A e B nos eixos, 15 min na célula A → B e uma configuração no contador | A tela contou uma configuração, mas exibiu apenas A e um traço na única célula. |

[Respostas simuladas e resultados observados](../sprint2/evidencias/us11/resultado-chrome.json)

### 3.2. Rastreabilidade e execução atual — `5abd06a`

Os identificadores executáveis reais são as tags e os nomes da feature; ela não possui tags `@CT` para US11. Os aliases históricos abaixo permitem comparar as rodadas sem criar IDs oficiais. Os novos ensaios `INV-*` são investigações/propostas de cobertura complementar, separadas dos casos oficiais.

| Critério / correção | Alias histórico | Cenário existente / fonte | Tipo da execução local | Resultado mais recente / evidência |
|---|---|---|---|---|
| 1. Consultar tempos direcionais cadastrados | CT-US11-01 | `@matriz-configurada`, `frontend/cypress/e2e/matriz-setup.feature:8–12` | Integrado: login, duas APIs e PostgreSQL reais; 30 min / 75 min | **Aprovado**; [resumo oficial](evidencias/us11/reavaliacao-5abd06a/cypress-us11-resumo.json), [JUnit](evidencias/us11/reavaliacao-5abd06a/cypress-us11-junit.xml); INV-01 complementa eixos/diagonais/contador. |
| 2. Informar ausência de configurações | CT-US11-02 | `@matriz-vazia`, feature:14–20 | Integrado: login, duas APIs e PostgreSQL reais, atualização com nova consulta | **Aprovado**; mesmos resumo/JUnit; INV-06 complementa atualização incorporando novos dados, com mocks. |
| BUG-001: destino ausente da lista | CT-US11-03 | `@bug001-destino-ausente`, feature:22–29 e issue #18 | Híbrido: preparação e login reais; respostas de famílias e setups simuladas nos steps:112–121 | **Aprovado**; resumo/JUnit oficiais; INV-02 confirma cabeçalhos e textos exatos. [Captura](evidencias/us11/reavaliacao-5abd06a/bug001-destino-ausente.png). |
| BUG-001: origem ausente da lista | CT-US11-04 | `@bug001-origem-ausente`, feature:31–39 e issue #18 | Híbrido: preparação e login reais; respostas de famílias e setups simuladas | **Aprovado**; resumo/JUnit oficiais; INV-03 confirma cabeçalhos e textos exatos. [Captura](evidencias/us11/reavaliacao-5abd06a/bug001-origem-ausente.png). |

Nos dois retestes, somente A ou somente B veio de `/api/families`, enquanto `/api/tempos-setup` trouxe A → B = 15 min com ambas as famílias. Obteve-se A e B nos dois eixos, `15 min` na direção A → B, `—` na inversa e `1 configuração`. As capturas foram obtidas nos ensaios complementares com **sessão e APIs simuladas**, não na execução integrada oficial. Não foi reproduzida a concorrência real entre dois planejadores sugerida na issue; foi verificada a renderização para o mesmo par de respostas que reproduzia o defeito anterior.

## 4. Bugs e pendências

### 4.1. Situação histórica — `4a50a6a`

| Issue / referência | Descrição | Classificação | Severidade | Status | Impacto no aceite |
|---|---|---|---|---|---|
| [BUG-001 · #18](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | A matriz conta a transição e omite o tempo quando falta a família de origem ou destino na lista de famílias. | Bug | Média | Reproduzido em `4a50a6a` | Afeta o cenário 1. |
| PR #16 | Falta adicionar à CI os dois casos de regressão do BUG-001. | Pendência da DoD | — | Pendente | Os testes atuais cobrem os fluxos nominais. |

**Situação do levantamento:** achados registrados.

### 4.2. Conciliação das pendências anteriores — `5abd06a`

| Pendência | Situação anterior | Situação atual | Evidência | Ação restante |
|---|---|---|---|---|
| BUG-001, destino e origem ausentes | Duas reproduções reprovadas | **Resolvida e verificada** no comportamento da interface | Código: `MatrizSetupPage.tsx:134–151,235,251,261`; dois cenários oficiais aprovados; INV-02/03, JUnit e capturas em 3.2 | Nenhum ajuste funcional demonstrado nesses cenários; encerramento administrativo da issue cabe à equipe e não foi realizado. |
| Incluir dois retestes do BUG-001 no Cypress/CI | Ausentes | **Resolvida e verificada** | Tags existentes na feature:22,31; herança de `@regressao`; execução local e JUnit remoto 4/4 por navegador | Proposta de fortalecer os steps para cabeçalhos/texto exato, sem tratar essa proposta como teste já incorporado. |
| Retestar a correção | Pendente para QA | **Resolvida e verificada** | Quatro cenários oficiais passaram, incluindo as duas variantes; ensaios complementares confirmam os detalhes | Preservar evidências e acompanhar futuras mudanças. |
| Validar dois cenários de aceite originais com backend | Aprovados anteriormente na CI | **Resolvida e verificada** para os critérios disponíveis | Dois cenários integrados passaram localmente no head; CI também registra os cenários no merge sintético | Confirmar que a definição oficial vigente não acrescenta critérios. |
| Atualizar matriz no estado vazio | Implementado e validado anteriormente | **Resolvida e verificada** | `@matriz-vazia` e INV-06 aprovados | Nenhuma no comportamento testado. |
| Executar carregamento e erro/recuperação | Apenas inspeção | **Resolvida e verificada**, limitada à UI com mocks | INV-04 e INV-05 aprovados; [JUnit de investigação](evidencias/us11/reavaliacao-5abd06a/investigacao-junit.xml) | Proposta de incorporar cobertura permanente; falhas reais de infraestrutura não foram induzidas. |
| Executar restrições de acesso | Inspeção e sessão simulada | **Parcialmente resolvida** | Login real de planejador; US02 4/4 e consulta de tempos negada para anônimo/operador na US10; INV-07 com sessão simulada; duas rotas inspecionadas | Para cobertura completa, executar menu e consulta de famílias com operador/anônimo reais no navegador. Não foram apresentados como testes já executados. |
| Código revisado e integrado via PR | PR aberto | **Ainda pendente** | Consulta ao PR #16: `state=open`, `merged=false`, head `5abd06a` | Equipe concluir o fluxo de revisão e integração; QA não aprovou nem fez merge. |
| Pipeline sem falhas | Atendido em `4a50a6a` | **Resolvida e verificada** na execução associada ao head atual | Run `45116249217`, cinco jobs verdes e logs por cenário; checkout do merge sintético `679dede` | Não confundir essa execução com checkout direto do head; execução local complementa essa evidência. |
| Documentação da matriz e dos testes | Atendida no relatório anterior | **Parcialmente resolvida** após inclusão dos novos retestes | README frontend descreve a função; guia Cypress omite os mocks dos retestes, conforme DOC-US11-01 | Atualizar guia dos testes para os quatro cenários e suas camadas. |
| Homologação e sua aplicabilidade na release | Não verificada | **Não foi possível verificar** | Não há URL, registro de deploy da US11 ou confirmação de exigência nos materiais consultados; plano de qualidade prevê ≥1 deploy/sprint nas Releases 2–4 | DevOps/PO confirmar aplicabilidade e fornecer versão/URL/evidência de deploy; então repetir smoke na versão implantada. |
| Aceite do PO | Sem evidência | **Não foi possível verificar** | PR e discussão consultados não trazem aceite explícito da US11 | PO registrar sua decisão; testes e parecer de QA não a substituem. |
| Definição vigente SC-28/DoD e IDs oficiais | IDs oficiais não confirmados; DoD atribuída à US | **Não foi possível verificar** integralmente | Plano disponível CT-01–CT-18, sem US11; fontes e limitação descritas em 1 | Disponibilizar SC-28 e acordos vigentes, confrontar critérios/DoD e atualizar rastreabilidade oficial. |

### 4.3. Novo achado documental e propostas

**DOC-US11-01 — guia não explicita a camada dos novos retestes (baixa severidade).** Reprodução por revisão estática: ler `frontend/cypress/README.md:3–6,85–100`, comparar com `matriz-setup.feature:22–39` e steps `matriz-setup.js:112–121`. **Esperado:** o guia distinguir os dois cenários nominais integrados dos dois retestes com respostas da matriz simuladas. **Obtido:** descreve os nominais e a suíte como usando APIs reais, sem explicar as interceptações com respostas dos retestes. **Impacto:** permite interpretar a validação do BUG-001 como reprodução integrada da concorrência real. A documentação foi classificada como parcialmente atualizada; este achado não demonstra falha funcional e, isoladamente, não impede o uso da matriz. A correção do guia cabe ao responsável; nesta tarefa foi atualizado somente o relatório de QA e suas evidências.

**Propostas de cobertura permanente, ainda não incluídas no plano:** incorporar os checks exatos dos cabeçalhos e células de INV-01/02/03 e os estados/recuperação de INV-04/05/06, mantendo os cenários existentes. Não foram criados IDs oficiais. Nenhum novo bug funcional foi confirmado no escopo executado; não se deduz ausência de defeitos fora dele.

## 5. Verificação da Definition of Done

### 5.1. Checklist histórico — `4a50a6a`

**Referência:** Definition of Done informada na US11.

| Critério da DoD | Situação | Evidência / pendência |
|---|---|---|
| Código revisado e integrado via Pull Request | Não atendido | Revisão feita, PR aberto. |
| Critérios de aceite atendidos e validados pelo QA | Não atendido | Cenários nominais passaram na CI. BUG-001 continua reproduzível. |
| Testes escritos e passando | Parcialmente atendido | Os dois testes de aceite da US11 passaram. Faltam os testes de regressão do BUG-001. |
| Pipeline de CI sem falha | Atendido | Cinco jobs passaram em `4a50a6a`, incluindo o aceite em Chrome e Electron. [CI do PR](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45063062507) |
| Implantado em ambiente de homologação, quando exigido na release | Não verificado | Exigência e implantação a confirmar. |
| Documentação atualizada | Atendido | Matriz e testes documentados nos READMEs do frontend e do Cypress. |
| Aceita pelo PO | Não verificado | Aceite sem evidência no PR consultado. |

### 5.2. Checklist da reavaliação — `5abd06a`

Mantidos os sete critérios herdados da avaliação anterior; a fonte específica vigente permanece a confirmar, conforme seção 1.

| Critério da DoD | Situação atual | Evidência / impedimento |
|---|---|---|
| Código revisado e integrado via Pull Request | **Não atendido** | Revisão e retestes feitos; PR #16 continua aberto e não integrado. |
| Critérios de aceite atendidos e validados pelo QA | **Parcialmente comprovado** | Os dois critérios disponíveis e correções do BUG-001 passaram; falta reconfirmar a definição integral vigente da SC-28. |
| Testes escritos e passando | **Atendido no escopo executado** | US11 4/4; regressão backend 33/33; US32 32/32 exemplos; CI com os quatro cenários por navegador. Investigações não substituem os testes oficiais. |
| Pipeline de CI sem falha | **Atendido para a execução consultada** | Cinco jobs com sucesso no run `45116249217`, associado ao head `5abd06a`, executando merge sintético `679dede`; logs/JUnit da US11 conferidos. |
| Implantado em homologação, quando exigido na release | **Não verificado** | Sem comprovação de exigência específica, URL ou deploy desta versão; plano geral prevê deploys nas Releases 2–4. |
| Documentação atualizada | **Parcialmente atendido** | Funcionalidade e evidências atualizadas; DOC-US11-01 pendente no guia Cypress. |
| Aceita pelo PO | **Não verificado** | Sem registro explícito acessível. Este relatório não constitui aceite do PO. |

## 6. Reteste e regressão

### 6.1. Rodada histórica — 22/11/2026, `4a50a6a`

O commit adicionou os testes nominais, o botão de atualização no estado vazio e seletores de teste. Os eixos continuam sendo montados exclusivamente com a lista de famílias. Nos dois retestes do bug, a tela contou uma configuração e omitiu os **15 min** de A → B. [Resultados completos](evidencias/us11/resultado-chrome-4a50a6a.json)

| Data | Tipo | Caso / fluxo | Bug relacionado | Commit | Resultado | Evidência |
|---|---|---|---|---|---|---|
| 22/11/2026 | Reteste | CT-US11-03 · Destino ausente | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | `4a50a6a` | Reprovado | [Captura](evidencias/us11/ct03-destino-ausente-4a50a6a.png) |
| 22/11/2026 | Reteste | CT-US11-04 · Origem ausente | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | `4a50a6a` | Reprovado | [Captura](evidencias/us11/ct04-origem-ausente-4a50a6a.png) |
| 22/11/2026 | Regressão | CT-US11-01 e CT-US11-02 · Fluxos nominais | — | `4a50a6a` | Aprovados | [Chrome local](evidencias/us11/resultado-chrome-4a50a6a.json) · [CI com backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45063062507) |

### 6.2. Nova execução local — 23/11/2026, `5abd06a`

**Ambiente e isolamento:** Windows `10.0.26200`; Python 3.11.9/pytest 8.4.2; Node 26.13.0/npm 11.20.0; Vite 8.3.5; Cypress 16.3.0; Chrome 157.0.8103.79 headless. Servidor PostgreSQL **18.6**, confirmado por `SELECT version()`, não apenas pela versão do cliente. Criado cluster próprio em `.tmp/qa-us11-5abd06a/pgdata`, escutando somente em `127.0.0.1:55433`, com os bancos novos `qa_us11_5abd06a_test` (Pytest) e `qa_us11_5abd06a_e2e_test` (Cypress/API). Migrations aplicadas nesses bancos; fixtures limpam exclusivamente essa massa. Nenhuma conexão de teste foi dirigida aos bancos existentes. Frontend: build desta versão servido por Vite preview na porta 5173; API na porta 8000 com `DB_*` apontando ao banco E2E. Não foi usado o `dist` anterior como evidência de versão. [Metadados](evidencias/us11/reavaliacao-5abd06a/ambiente.json).

**Comandos principais**, executados a partir da raiz ou das pastas indicadas; configuração de conexão exclusiva conforme acima, sem publicar credenciais:

```powershell
# Raiz: criar cluster próprio e os dois bancos (binários do PostgreSQL 18).
& 'C:/Program Files/PostgreSQL/18/bin/initdb.exe' -D .tmp/qa-us11-5abd06a/pgdata -U qa_us11 --auth=trust --encoding=UTF8 --no-locale
& 'C:/Program Files/PostgreSQL/18/bin/pg_ctl.exe' -D .tmp/qa-us11-5abd06a/pgdata -l .tmp/qa-us11-5abd06a/postgres.log -o '-h 127.0.0.1 -p 55433' -w start
& 'C:/Program Files/PostgreSQL/18/bin/createdb.exe' -h 127.0.0.1 -p 55433 -U qa_us11 qa_us11_5abd06a_test
& 'C:/Program Files/PostgreSQL/18/bin/createdb.exe' -h 127.0.0.1 -p 55433 -U qa_us11 qa_us11_5abd06a_e2e_test

# backend, com DB_* do banco E2E; serviços iniciados em processos ocultos.
./.venv/Scripts/python.exe -m alembic upgrade head
./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# TEST_DATABASE_URL seleciona o banco Pytest separado.
./.venv/Scripts/python.exe -m pytest -v --junitxml=../.tmp/qa-us11-5abd06a/pytest.xml testes/integration/test_us05_families.py testes/integration/test_us10_tempos_setup.py testes/integration/test_us02_access_control.py testes/unit/test_seed_e2e.py

# frontend
npm.cmd run lint
npm.cmd run build
node.exe node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 5173 --strictPort
# E2E_PYTHON: caminho absoluto de backend/.venv/Scripts/python.exe.
# E2E_DATABASE_URL e DB_*: banco E2E exclusivo, porta 55433.
# E2E_ARTIFACTS_DIR: .tmp/qa-us11-5abd06a/cypress-chrome e /cypress-us32, respectivamente.
npm.cmd run test:e2e -- --browser chrome --tags '@US11'
npm.cmd run test:e2e -- --browser chrome --tags '@US32'

# Investigação temporária independente, com sessão e APIs simuladas.
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
node.exe node_modules/cypress/bin/cypress run --config-file ../.tmp/qa-us11-5abd06a/cypress-investigacao.config.cjs --browser chrome
```

| Execução / seleção e justificativa | Resultado | Natureza e evidência |
|---|---|---|
| US11: quatro cenários existentes — dois critérios originais e dois retestes | **4/4 aprovados**, 0 falhas, 0 pendentes, 0 ignorados; 5.989 ms de execução da spec | Dois integrados e dois híbridos, descritos em 3.2. [Resumo](evidencias/us11/reavaliacao-5abd06a/cypress-us11-resumo.json), [JUnit](evidencias/us11/reavaliacao-5abd06a/cypress-us11-junit.xml), [log](evidencias/us11/reavaliacao-5abd06a/cypress-chrome.log). |
| Backend: US05 (7), US10 (16), US02 (4) — dados e permissões consumidos pela matriz | **27/27 aprovados** | Integração TestClient/FastAPI/PostgreSQL real; verificações de listagem, payloads, persistência, direcionalidade e 401/403 da consulta de setups. [JUnit](evidencias/us11/reavaliacao-5abd06a/pytest.xml), [log](evidencias/us11/reavaliacao-5abd06a/pytest.log). |
| Proteções da preparação E2E (6) — isolamento do banco usado pelos hooks | **6/6 aprovados** | Unitários com mocks de proteção antes de abrir conexão; não são seis testes integrados. Mesmo JUnit; total Pytest: 33, em 6,22 s. |
| US32: tags existentes CT32–CT43 — convivência dos hooks e fixtures compartilhados | **32/32 exemplos aprovados** | Suite oficial integrada, com seus testes de sessão/API/UI e exemplos parametrizados. Não são 32 novos IDs nem casos US11. [Resumo](evidencias/us11/reavaliacao-5abd06a/cypress-us32-resumo.json), [JUnit](evidencias/us11/reavaliacao-5abd06a/cypress-us32-junit.xml), [log](evidencias/us11/reavaliacao-5abd06a/cypress-us32.log). |
| INV-01 a INV-07 — complementação explícita de asserções e estados antes não executados | **7/7 aprovados** na execução final | Ensaio temporário com sessão e APIs simuladas: nominal original, destino ausente, origem ausente, carregamento, erro 500/recuperação, vazio → preenchido e menu do operador. [JUnit](evidencias/us11/reavaliacao-5abd06a/investigacao-junit.xml), [log](evidencias/us11/reavaliacao-5abd06a/investigacao-final.log), [fonte arquivada, fora da suíte](evidencias/us11/reavaliacao-5abd06a/investigacao.cy.js.txt), [configuração arquivada](evidencias/us11/reavaliacao-5abd06a/cypress-investigacao.config.cjs.txt). |
| Lint e build do frontend | **Aprovados**, exit code 0 | [Lint](evidencias/us11/reavaliacao-5abd06a/lint.log), [build concluído](evidencias/us11/reavaliacao-5abd06a/build-escalated.log). São verificações estáticas/compilação, não casos funcionais. |

**Intercorrências de infraestrutura:** a primeira tentativa de iniciar PostgreSQL falhou no sandbox (`could not create restricted token`, códigos 87/3); a inicialização fora do sandbox funcionou. O primeiro build falhou por `spawn EPERM` e carregamento da dependência nativa; o mesmo comando fora do sandbox passou sem alteração de fontes/dependências ([log inicial](evidencias/us11/reavaliacao-5abd06a/build.log)). O primeiro lançamento direto da investigação encerrou antes de gerar resultados (`-1073741795`); removida a variável herdada `ELECTRON_RUN_AS_NODE` apenas do processo de teste, a repetição passou. A investigação foi repetida para ajustar o tamanho da janela das capturas e continuou 7/7; isso não adiciona novos casos ao resumo. Nenhuma dessas tentativas foi contabilizada como reprovação funcional. Dependências já instaladas foram utilizadas; não se afirma execução local de `npm ci`.

**Encerramento e preservação:** API e preview criados pela avaliação foram encerrados após conferir seus processos, e o cluster exclusivo foi parado com `pg_ctl -D .tmp/qa-us11-5abd06a/pgdata -m fast -w stop`. Arquivos temporários permanecem em `.tmp`, ignorado pelo Git. As fontes dos ensaios estão arquivadas como `.txt` nas evidências; para repetir em outra cópia, restaurá-las com os nomes originais sob `.tmp/qa-us11-5abd06a/` antes de executar o comando de investigação. Resumos oficiais registram árvore limpa e o mesmo hash de fontes antes da edição documental; hashes dos arquivos preservados constam no [manifesto](evidencias/us11/reavaliacao-5abd06a/manifesto.json).

### 6.3. CI consultada e limites da evidência remota

Run [45116249217](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45116249217), associado pela API ao head completo `5abd06aa481e55828e8ce41680ea38aad5c3bc65`: cinco jobs concluídos com sucesso. Foram lidos os logs de aceite [Chrome, job 137499659430](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45116249217/job/137499659430) e [Electron, job 137499659486](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45116249217/job/137499659486). Ambos incluem os quatro nomes da US11 no JUnit, quatro aprovações sem falhas, mais 32 exemplos da US32 aprovados. Ambiente remoto registrado nos logs: Ubuntu 26.04.1, Node 22.23.5, Cypress 16.3.0, Chrome 157/Electron 150; o workflow fornece PostgreSQL 18 por serviço isolado por job.

**Checkout efetivamente testado pela CI:** `679dedec9e26ef6cd682963cd02afcb1c3e54933`, merge sintético do head `5abd06a` na base `5cf655e`, confirmado pela linha `HEAD is now at ... Merge 5abd06aa... into 5cf655ee...` e `git log -1 --format=%H`. Portanto, a CI comprova essa composição do PR e os testes locais comprovam o head diretamente. A conclusão não depende apenas do selo verde. Não foram baixados os vídeos remotos nem auditadas integralmente as suítes fora da US11; os resultados remotos citados são os observados nos logs/JUnit incorporados ao [snapshot](evidencias/us11/reavaliacao-5abd06a/github-ci.json).

### 6.4. Validações restantes e roteiro posterior

Obter SC-28/DoD vigentes do PO e comparar cada item com 3.2/5.2, criando **propostas** identificadas para qualquer cenário adicional; não foi possível executar critérios cujo conteúdo não está disponível. DevOps deve confirmar a exigência de homologação e fornecer URL e commit implantado; então repetir login de planejador, matriz com valores direcionais, estado vazio/atualização e acesso com operador. Para ampliar a verificação de permissões, usar as contas reais do banco E2E, confirmar ausência do menu para operador e HTTP 401/403 em **ambas** as consultas, incluindo famílias; os bloqueios reais já exercitados na US10 não comprovam automaticamente os de famílias. A eventual reprodução da intercalação de consultas com cadastros concorrentes exige ensaio integrado específico, separado dos retestes com mocks.

O plano de qualidade registra Q-07 (p95 ≤ 2 s) e métricas de homologação em nível de release. Não foram medidas nesta tarefa nem consideradas satisfeitas pelos tempos de execução das suítes; não foram identificadas como driver específico da US11. Manter a validação dessas metas na avaliação correspondente da release, sem substituí-las por médias ou pelo tempo desta spec. Confirmar aplicabilidade com PO/QA ao recuperar a fonte oficial.

## 7. Resumo dos resultados

### 7.1. Resumo histórico — `4a50a6a`

| Indicador | Quantidade |
|---|---:|
| Casos distintos na rodada de `4a50a6a` | 4 |
| Casos aprovados | 2 |
| Casos reprovados | 2 |
| Casos bloqueados | 0 |
| Casos não executados na rodada registrada | 0 |
| Bugs identificados | 1 |
| Bugs corrigidos com reteste aprovado | 0 |
| Bugs pendentes | 1 |

### 7.2. Resumo vigente — `5abd06a`, 23/11/2026

Cada cenário US11 é contado uma vez pelo resultado mais recente. A repetição em CI, os retestes e as investigações que repetem o comportamento não aumentam a quantidade de casos da US11.

| Indicador do escopo US11 conhecido | Quantidade / situação |
|---|---:|
| Cenários existentes da feature / aliases históricos avaliados | 4 |
| Aprovados na última execução local | 4 |
| Reprovados na última execução local | 0 |
| Bloqueados entre esses quatro cenários conhecidos | 0 |
| Não executados entre esses quatro cenários conhecidos | 0 |
| Bugs funcionais históricos reavaliados | 1 |
| Bugs funcionais resolvidos com reteste aprovado | 1 |
| Bugs funcionais ainda reproduzidos nesse escopo | 0 |
| Novos bugs funcionais confirmados nessa rodada | 0 |
| Novo achado documental | 1 — DOC-US11-01 |
| Critérios herdados da DoD | 7: 2 atendidos no escopo, 2 parcialmente comprovados/atendidos, 1 não atendido, 2 não verificados |
| Total oficial de casos/critério integral vigente da SC-28 | **Não levantado na fonte oficial**; não representado por zero |

**Regressão separada:** 27 testes integrados do backend + 6 unitários de proteção, todos aprovados; US32 CT32–CT43 com 32 exemplos aprovados. **Investigação separada:** 7 ensaios temporários aprovados, sem incorporação ao plano. Não se soma tudo como casos novos da US11 e não se calcula cobertura integral de requisitos sem a definição oficial.

## 8. Parecer do QA

### 8.1. Parecer histórico — `4a50a6a`

**Pendente de ajustes em `4a50a6a`.** Os dois fluxos nominais passaram, mas o BUG-001 continua impedindo o aceite do cenário com dados.

| Pendência | Responsável | Referência | Situação |
|---|---|---|---|
| Corrigir os eixos e adicionar testes de regressão para origem e destino ausentes | @arthur-marqs | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | Pendente |
| Retestar os dois casos do BUG-001 após a correção | QA | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) | Pendente |

**Limitação remanescente:** o BUG-001 foi reproduzido com respostas simuladas. O aceite do PO segue pendente.

### 8.2. Parecer da reavaliação — `5abd06a`

**Pendente de ajustes — conclusão da DoD.** O BUG-001 está **resolvido e verificado** nas duas variantes do comportamento da interface; os quatro cenários existentes da US11 e a regressão selecionada passaram. O motivo funcional que sustentava o parecer anterior deixou de ser reproduzido. Não foi encontrada falha funcional impeditiva nos cenários executados.

A DoD herdada exige código revisado **e integrado via PR**, e o PR #16 continua comprovadamente aberto/não integrado. Esse critério permanece **não atendido**, independentemente dos testes aprovados. A documentação dos novos retestes está parcialmente atualizada (DOC-US11-01). Além dessas pendências verificadas, a **validação integral permanece inconclusiva** quanto à definição vigente SC-28/DoD, aplicabilidade/evidência de homologação e aceite do PO, por falta de fontes ou registros essenciais. Assim, não há evidência suficiente para declarar “Apta para aceite” da US integralmente.

| Ação restante | Responsável / papel | Condição de conclusão |
|---|---|---|
| Concluir revisão e integração do PR pelo fluxo da equipe | Desenvolvedor / revisores | Registro de integração e commit resultante; esta tarefa não autoriza nem realiza merge ou aprovação. |
| Explicitar os quatro cenários e a camada dos mocks no guia | Desenvolvedor | Documentação coerente com feature/steps, sem afirmar concorrência integrada não executada. |
| Confirmar SC-28, DoD vigente e rastreabilidade oficial | PO / QA | Fonte oficial acessível e confronto dos critérios com os testes/evidências. |
| Confirmar exigência e comprovar homologação da versão | PO / DevOps / QA | Registro de deploy aplicável, versão identificada e smoke registrado. |
| Decidir e registrar aceite da US | PO | Decisão explícita após análise dos resultados e pendências. |

Este parecer é de QA e não substitui o aceite do PO. A issue #18 permaneceu aberta durante a consulta; isso não foi usado como evidência de persistência do bug. Não foram publicados comentários, alteradas issues, aprovados PRs, feitos commits, push ou merge.

## 9. Histórico da revisão

| Data | Responsável | Commit avaliado | Atualização |
|---|---|---|---|
| 22/11/2026 | QA da US11 | `8de6f4a` | Revisão inicial, validação dos fluxos nominais e reprodução do BUG-001 no Chrome. |
| 22/11/2026 | QA da US11 | `4a50a6a` | CI validada. BUG-001 reproduzido com origem e destino ausentes em execuções separadas. |
| 23/11/2026 | Reavaliação assistida de QA | `5abd06aa481e55828e8ce41680ea38aad5c3bc65` | Histórico preservado; BUG-001 resolvido nas duas variantes; US11 4/4, backend 33/33, US32 32/32 exemplos e investigação 7/7. Logs da CI conferidos no merge sintético `679dede`. Parecer pendente pela conclusão da DoD; fontes vigentes/homologação/PO não comprovados. |
