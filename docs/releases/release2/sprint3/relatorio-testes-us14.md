
# Relatório de testes — US14: Considerar prazos e prioridades no sequenciamento

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável | Luiz Inácio Moura da Costa |
| Data | 25/11/2026 |
| História de usuário | US14 |
| Branch | `feature/us14-prazos-prioridades` |
| Pull Request | Pendente |
| Situação | Testes locais aprovados |

## 1. Objetivo e escopo

Validar o sequenciamento de ordens de produção considerando os prazos, as prioridades, as durações estimadas e os tempos de setup entre famílias de produtos.

A implementação complementa o algoritmo da US13, permitindo considerar a urgência das ordens mesmo quando isso resulta em um aumento no tempo total de setup.

## 2. Implementação

As principais alterações realizadas foram:

- Inclusão dos prazos, prioridades e durações estimadas no algoritmo de sequenciamento.
- Comparação de diferentes alternativas de sequência.
- Consideração da quantidade de ordens atrasadas e do impacto dos atrasos por prioridade.
- Validação dos dados necessários para gerar a sugestão.
- Preservação do comportamento anterior quando não existem dados de prazo ou prioridade.
- Adequação da restrição do banco de dados para permitir sugestões com maior tempo de setup quando necessário.

A migration `6b14a2e9c703` foi aplicada com sucesso.

## 3. Validação funcional

Os identificadores abaixo correspondem aos cenários implementados para a US14.

| Caso | Cenário | Resultado esperado | Resultado |
|---|---|---|---|
| US14_CT01 | Ordem urgente com aumento de setup | Priorizar a ordem urgente mesmo quando a sequência apresenta maior tempo de setup | Aprovado |
| US14_CT02 | Prazos diferentes e mesma prioridade | Considerar os prazos na definição da sequência | Aprovado |
| US14_CT03 | Prioridades diferentes e mesmo prazo | Considerar as prioridades na definição da sequência | Aprovado |
| US14_CT04 | Dados de planejamento incompletos | Impedir a geração da sugestão e informar a pendência | Aprovado |

### Evidências

- [US14_CT01](evidencias/us14/US14_CT01.png)
- [US14_CT02](evidencias/us14/US14_CT02.png)
- [US14_CT03](evidencias/us14/US14_CT03.png)
- [US14_CT04](evidencias/us14/US14_CT04.png)
- [Resumo Cypress US14](evidencias/us14/chrome-us14-resumo.json)
- [JUnit Cypress US14](evidencias/us14/chrome-us14-junit.xml)

## 4. Testes automatizados

| Tipo de teste | Executados | Aprovados | Reprovados |
|---|---:|---:|---:|
| Testes unitários US14 | 4 | 4 | 0 |
| Testes de integração US14 | 5 | 5 | 0 |
| Cypress US14 | 4 | 4 | 0 |
| Regressão completa do backend | 222 | 222 | 0 |
| Regressão completa Cypress Chrome | 53 | 53 | 0 |

Os testes específicos da US14 também estão incluídos nas respectivas suítes de regressão, portanto não devem ser somados novamente ao total.

### 4.1. Regressão do backend

A suíte completa do Pytest foi executada em um banco exclusivo de testes.

- Resultado: 222 testes aprovados.
- Duração: 298,33 segundos.
- [Relatório XML](evidencias/us14/pytest-backend.xml)

### 4.2. Regressão do frontend

A regressão foi executada utilizando Cypress 16.3.0 e Chrome 158 em modo headless.

| Feature | Executados | Aprovados |
|---|---:|---:|
| Matriz de setup | 4 | 4 |
| Prazos e prioridades | 4 | 4 |
| Sequência sugerida | 13 | 13 |
| Gerenciamento de usuários | 32 | 32 |
| Total | 53 | 53 |

Tempo total de execução: 22 minutos e 27 segundos.

Evidências:

- [Resumo da regressão](evidencias/us14/chrome-regressao-resumo.json)
- [JUnit — Matriz de setup](evidencias/us14/regressao-matriz-setup.xml)
- [JUnit — Prazos e prioridades](evidencias/us14/regressao-prazos-prioridades.xml)
- [JUnit — Sequência sugerida](evidencias/us14/regressao-sugestao.xml)
- [JUnit — Gerenciamento de usuários](evidencias/us14/regressao-usuarios.xml)

### 4.3. Verificações adicionais

| Verificação | Resultado |
|---|---|
| Build do frontend | Aprovado |
| ESLint | Aprovado |
| Git diff --check | Aprovado |
| Alembic upgrade head | Aprovado |

## 5. Problemas encontrados e resolvidos

| Problema | Solução | Situação |
|---|---|---|
| Restrição do banco impedia sugestões com aumento de setup | Atualização do model e criação de migration | Resolvido |
| Dependências incompletas do frontend | Reinstalação das dependências com npm ci | Resolvido |
| Banco exclusivo do Cypress inexistente | Criação do banco e aplicação das migrations | Resolvido |

A primeira execução do Cypress apresentou falhas durante a preparação do ambiente devido à ausência do banco de testes. Após a configuração, os quatro cenários da US14 e a regressão completa foram aprovados.

Nenhum defeito funcional permaneceu identificado nos cenários executados.

## 6. Ambiente de testes

- Sistema operacional: Windows 10.
- Banco de dados: PostgreSQL 18.
- Backend: Python, FastAPI e Pytest.
- Frontend: React, TypeScript e Vite.
- Testes E2E: Cypress 16.3.0 e Chrome 158.
- Banco do Pytest: `setupflow_test`.
- Banco do Cypress: `setupflow_e2e_test`.

Os bancos utilizados nos testes são separados do banco de desenvolvimento.

## 7. Definition of Done

| Critério | Situação |
|---|---|
| Implementação da história de usuário | Concluída |
| Testes automatizados escritos e aprovados | Concluído |
| Validação funcional local | Concluída |
| Evidências de testes registradas | Concluído |
| Documentação técnica atualizada | Em andamento |
| Revisão e integração via Pull Request | Pendente |
| Pipeline de CI sem falhas | Pendente |
| Homologação, quando exigida | Pendente de confirmação |
| Aceite do Product Owner | Pendente |

## 8. Conclusão

Os testes realizados demonstraram que o sequenciamento passou a considerar prazos e prioridades, mantendo o funcionamento das funcionalidades anteriores nos cenários de regressão executados.

A regressão do backend apresentou 222 testes aprovados, enquanto a regressão do Cypress no Chrome apresentou 53 cenários aprovados, sem falhas.

A implementação está apta para seguir para a revisão de código. A validação no Electron, a execução da CI, a revisão pelos demais integrantes e o aceite do Product Owner ainda estão pendentes.
