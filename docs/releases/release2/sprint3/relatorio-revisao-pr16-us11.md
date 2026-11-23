# Relatório de revisão e validação — US11: Visualizar matriz de setup

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável pelo QA | @leonardo-istamilo |
| Data da revisão | 22/11/2026 |
| História de usuário | SC-28 / US11 — Visualizar matriz de setup |
| Pull Request | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) |
| Branch | `feature/US11-matriz-setup` |
| Commit avaliado | `4a50a6a` (revisão inicial em `8de6f4a`) |
| Ambiente | Local, Windows, Chrome 157.0.8103.79 em modo headless |
| Parecer do QA | **Pendente de ajustes** |

## 1. Objetivo e escopo

Verificar a matriz de setup, os dois cenários de aceite e a Definition of Done da US11. A revisão abrangeu o acesso pelo perfil `PLANEJADOR`, os tempos direcionais entre famílias e o estado sem configurações.

**Dependência:** APIs de famílias e tempos de setup já disponíveis. **Drivers relacionados:** nenhum identificado no escopo da avaliação.

**Limitações:** o reteste do BUG-001 simulou a sessão e as APIs. Os dois cenários nominais foram executados com o backend na CI.

## 2. Revisão da implementação

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

## 3. Validação dos critérios de aceite

Os identificadores abaixo são locais a este relatório. Os IDs oficiais do plano de testes não foram confirmados.

| Critério / cenário | Caso de teste | Execução | Resultado | Evidência / bug |
|---|---|---|---|---|
| 1. Exibir famílias e tempos cadastrados | CT-US11-01 | Automatizada no Chrome, APIs simuladas | Aprovado no fluxo nominal | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 2. Informar que não há configurações | CT-US11-02 | Automatizada no Chrome, APIs simuladas | Aprovado | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 1. Exibir uma transição cuja família de destino está ausente da lista de famílias | CT-US11-03 | Automatizada no Chrome, APIs simuladas | Reprovado | [Captura](../sprint2/evidencias/us11/ct03-matriz-setup-chrome.png) · [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) |

Os passos abaixo preservam a rodada inicial. A execução mais recente, em `4a50a6a`, está na seção de reteste e regressão.

### 3.1. Registro de execução

**Data / responsável:** 22/11/2026 · QA da US11. **Commit:** `8de6f4a`.

Em cada caso, a execução configurou os retornos simulados de sessão, famílias e tempos, abriu **Matriz de setup** pelo menu lateral e verificou os eixos, as células, o contador ou a mensagem de estado vazio.

| Caso | Pré-condições e dados | Resultado esperado | Resultado obtido |
|---|---|---|---|
| CT-US11-01 | Sessão de planejador, famílias A e B, A → B = 15 min e B → A = 30 min | Ambas as famílias nos eixos, valores nas direções corretas e duas configurações | Os valores, os eixos e o contador conferiram. |
| CT-US11-02 | Sessão de planejador, famílias A e B, lista de setups vazia | Mensagem de ausência de configurações | A tela exibiu **“Nenhuma configuração de setup cadastrada”**. |
| CT-US11-03 | Sessão de planejador, lista de famílias contendo apenas A, setup A → B = 15 min | A e B nos eixos, 15 min na célula A → B e uma configuração no contador | A tela contou uma configuração, mas exibiu apenas A e um traço na única célula. |

[Respostas simuladas e resultados observados](../sprint2/evidencias/us11/resultado-chrome.json)

## 4. Bugs e pendências

| Issue / referência | Descrição | Classificação | Severidade | Status | Impacto no aceite |
|---|---|---|---|---|---|
| [BUG-001 · #18](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | A matriz conta a transição e omite o tempo quando falta a família de origem ou destino na lista de famílias. | Bug | Média | Reproduzido em `4a50a6a` | Afeta o cenário 1. |
| PR #16 | Falta adicionar à CI os dois casos de regressão do BUG-001. | Pendência da DoD | — | Pendente | Os testes atuais cobrem os fluxos nominais. |

**Situação do levantamento:** achados registrados.

## 5. Verificação da Definition of Done

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

## 6. Reteste e regressão

O commit adicionou os testes nominais, o botão de atualização no estado vazio e seletores de teste. Os eixos continuam sendo montados exclusivamente com a lista de famílias. Nos dois retestes do bug, a tela contou uma configuração e omitiu os **15 min** de A → B. [Resultados completos](evidencias/us11/resultado-chrome-4a50a6a.json)

| Data | Tipo | Caso / fluxo | Bug relacionado | Commit | Resultado | Evidência |
|---|---|---|---|---|---|---|
| 22/11/2026 | Reteste | CT-US11-03 · Destino ausente | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | `4a50a6a` | Reprovado | [Captura](evidencias/us11/ct03-destino-ausente-4a50a6a.png) |
| 22/11/2026 | Reteste | CT-US11-04 · Origem ausente | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | `4a50a6a` | Reprovado | [Captura](evidencias/us11/ct04-origem-ausente-4a50a6a.png) |
| 22/11/2026 | Regressão | CT-US11-01 e CT-US11-02 · Fluxos nominais | — | `4a50a6a` | Aprovados | [Chrome local](evidencias/us11/resultado-chrome-4a50a6a.json) · [CI com backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45063062507) |

## 7. Resumo dos resultados

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

## 8. Parecer do QA

**Pendente de ajustes em `4a50a6a`.** Os dois fluxos nominais passaram, mas o BUG-001 continua impedindo o aceite do cenário com dados.

| Pendência | Responsável | Referência | Situação |
|---|---|---|---|
| Corrigir os eixos e adicionar testes de regressão para origem e destino ausentes | @arthur-marqs | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | Pendente |
| Retestar os dois casos do BUG-001 após a correção | QA | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) | Pendente |

**Limitação remanescente:** o BUG-001 foi reproduzido com respostas simuladas. O aceite do PO segue pendente.

## 9. Histórico da revisão

| Data | Responsável | Commit avaliado | Atualização |
|---|---|---|---|
| 22/11/2026 | QA da US11 | `8de6f4a` | Revisão inicial, validação dos fluxos nominais e reprodução do BUG-001 no Chrome. |
| 22/11/2026 | QA da US11 | `4a50a6a` | CI validada. BUG-001 reproduzido com origem e destino ausentes em execuções separadas. |
