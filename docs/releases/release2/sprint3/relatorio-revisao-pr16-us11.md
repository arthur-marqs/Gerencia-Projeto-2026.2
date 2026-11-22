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
| Commit avaliado | `8de6f4a`. O commit `bfb797f` acrescentou somente as evidências. |
| Ambiente | Local, Windows, Chrome 157.0.8103.79 em modo headless |
| Parecer do QA | **Pendente de ajustes** |

## 1. Objetivo e escopo

Verificar a matriz de setup, os dois cenários de aceite e a Definition of Done da US11. A revisão abrangeu o acesso pelo perfil `PLANEJADOR`, os tempos direcionais entre famílias e o estado sem configurações.

**Dependência:** APIs de famílias e tempos de setup já disponíveis. **Drivers relacionados:** nenhum identificado no escopo da avaliação.

**Limitações:** a execução no Chrome simulou a sessão e as respostas das APIs. A validação integrada com o backend segue pendente.

## 2. Revisão da implementação

| Aspecto | Situação | Observações / evidências |
|---|---|---|
| Comportamento previsto na US | Não conforme | A matriz pode contar uma transição e omitir seu tempo. [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) |
| Regras de negócio | Conforme no fluxo nominal | Linhas são origens, colunas são destinos e os tempos aparecem em minutos. |
| Permissões de acesso | Conforme por revisão de código | Menu, página e endpoints exigem `PLANEJADOR`. A execução utilizou uma sessão simulada desse perfil. |
| Validações e tratamento de erros | Não verificado em execução | O código prevê mensagem de erro e nova tentativa. |
| Estados da interface | Parcialmente verificado | Estado vazio confirmado no Chrome. Carregamento e erro identificados por inspeção. |
| Testes automatizados relacionados | Não conforme | O PR não inclui cenários Cypress/Cucumber da US11. |
| Documentação exigida | Não conforme | Falta incluir a matriz no README do frontend. |

O PR está aberto e o GitHub o indica como mesclável com `main`. Lint e build passaram localmente. [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16)

## 3. Validação dos critérios de aceite

Os identificadores abaixo são locais a este relatório. Os IDs oficiais do plano de testes não foram confirmados.

| Critério / cenário | Caso de teste | Execução | Resultado | Evidência / bug |
|---|---|---|---|---|
| 1. Exibir famílias e tempos cadastrados | CT-US11-01 | Automatizada no Chrome, APIs simuladas | Aprovado no fluxo nominal | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 2. Informar que não há configurações | CT-US11-02 | Automatizada no Chrome, APIs simuladas | Aprovado | [Resultados](../sprint2/evidencias/us11/resultado-chrome.json) |
| 1. Exibir uma transição cuja família de destino está ausente da lista de famílias | CT-US11-03 | Automatizada no Chrome, APIs simuladas | Reprovado | [Captura](../sprint2/evidencias/us11/ct03-matriz-setup-chrome.png) · [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) |

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
| [BUG-001 · #18](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | A matriz conta uma transição e omite seu tempo se uma família estiver ausente dos eixos. | Bug | Média | Confirmado no Chrome com APIs simuladas | Afeta o cenário 1. |
| PR #16 | Faltam os testes de aceite e regressão da US11 na CI. | Pendência da DoD | — | Pendente | Falta cobertura automatizada da funcionalidade. |
| PR #16 | Falta documentar a matriz no README. | Pendência da DoD | — | Pendente | Item de documentação em aberto. |
| PR #16 | O botão **Atualizar matriz** fica indisponível no estado vazio. | Melhoria | — | Opcional | O cenário 2 já apresenta a mensagem esperada. |

**Situação do levantamento:** achados registrados.

## 5. Verificação da Definition of Done

**Referência:** Definition of Done informada na US11.

| Critério da DoD | Situação | Evidência / pendência |
|---|---|---|
| Código revisado e integrado via Pull Request | Não atendido | Revisão feita, PR aberto. |
| Critérios de aceite atendidos e validados pelo QA | Não atendido | BUG-001 pendente. Falta validar com o backend. |
| Testes escritos e passando | Não atendido | Faltam testes automatizados da US11 na suíte do projeto. |
| Pipeline de CI sem falha | Atendido | CI verde no commit de implementação e no commit de evidências. [CI de `8de6f4a`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/43152447338) · [CI de `bfb797f`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45057136300) |
| Implantado em ambiente de homologação, quando exigido na release | Não verificado | Exigência e implantação a confirmar. |
| Documentação atualizada | Não atendido | README do frontend pendente. |
| Aceita pelo PO | Não verificado | Aceite sem evidência no PR consultado. |

## 6. Reteste e regressão

Após a correção, retestar com a família de destino e com a família de origem ausentes da lista. Repetir os fluxos preenchido e vazio para verificar a direção dos tempos e a mensagem de ausência. Ambos usam a montagem da matriz alterada pela correção.

| Data | Tipo | Caso / fluxo | Bug relacionado | Commit | Resultado | Evidência |
|---|---|---|---|---|---|---|
| — | Reteste | Família de origem ou de destino ausente | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | A definir | Não executado | — |
| — | Regressão após a correção | CT-US11-01 e CT-US11-02 | — | A definir | Não executado | — |

## 7. Resumo dos resultados

| Indicador | Quantidade |
|---|---:|
| Casos previstos na rodada registrada | 3 |
| Casos aprovados | 2 |
| Casos reprovados | 1 |
| Casos bloqueados | 0 |
| Casos não executados na rodada registrada | 0 |
| Bugs identificados | 1 |
| Bugs corrigidos com reteste aprovado | 0 |
| Bugs pendentes | 1 |

## 8. Parecer do QA

**Pendente de ajustes em `8de6f4a`.** Os dois fluxos nominais passaram com APIs simuladas. O BUG-001 impede o aceite do cenário com dados, pois uma transição contabilizada pode ficar invisível.

| Pendência | Responsável | Referência | Situação |
|---|---|---|---|
| Corrigir os eixos e adicionar testes de regressão para origem e destino ausentes | @arthur-marqs | [BUG-001](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/18) | Pendente |
| Incluir os cenários de aceite no Cypress/Cucumber e atualizar o README | @arthur-marqs | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) | Pendente |
| Retestar a correção e validar com o backend | QA | [PR #16](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16) | Pendente |

**Limitação remanescente:** as respostas simuladas confirmam o comportamento do frontend. A validação com backend real e o aceite do PO ainda estão pendentes.

## 9. Histórico da revisão

| Data | Responsável | Commit avaliado | Atualização |
|---|---|---|---|
| 22/11/2026 | QA da US11 | `8de6f4a` | Revisão inicial, validação dos fluxos nominais e reprodução do BUG-001 no Chrome. |
