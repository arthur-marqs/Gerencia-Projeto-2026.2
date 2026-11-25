# Relatório de testes — US15: Considerar compatibilidade entre produtos e máquinas no sequenciamento

| Informação | Detalhe |
|---|---|
| Projeto | SetupFlow |
| Release / Sprint | Release 2 / Sprint 3 |
| Responsável | Luiz Inácio Moura da Costa |
| Data | 25/11/2026 |
| História de usuário | US15 — SC-32 |
| Branch | `feature/SC-32-us15-compatibilidade-sequenciamento` |
| Pull Request | Pendente |
| Situação | Validação local concluída; revisão e CI pendentes |

## 1. Objetivo e escopo

Validar a atribuição de ordens de produção a máquinas compatíveis e ativas,
impedindo a geração da sugestão quando não houver uma máquina disponível segundo
os critérios de compatibilidade e atividade. A US15 complementa as US13 e US14,
preservando as regras de setup, prazo e prioridade no sequenciamento de cada máquina.

## 2. Implementação

- Distribuição de ordens entre máquinas compatíveis e ativas, escolhendo a máquina com menos ordens atribuídas e desempate pelo código.
- Sequenciamento independente por máquina, com setup zero na primeira ordem e sem troca entre máquinas distintas.
- Validação de família, compatibilidade, tempos de setup e dados de urgência antes de gravar a sugestão.
- Persistência e apresentação da máquina atribuída em cada item da sequência sugerida.
- Preservação da máquina registrada no histórico e das posições originais das ordens.
- Integração com as regras de prazo e prioridade da US14 aprovadas pelo PO e incorporadas à `main` pelo PR #23.

A migration `7c15a3e9d204` adiciona a referência à máquina nos itens da sugestão.
A migration `b872837156bd` une as revisões da US14 e da US15. Os dois bancos
exclusivos de testes foram atualizados até essa revisão com sucesso.

A distribuição é uma heurística por quantidade de ordens, não uma otimização
global por duração ou capacidade. O cálculo considera produção contínua, com
um mesmo horário inicial para as máquinas, sem turnos ou pausas.

## 3. Validação funcional

| Caso | Cenário | Resultado esperado | Resultado |
|---|---|---|---|
| US15_CT01 | Ordens compatíveis com máquinas diferentes | Atribuir cada ordem à máquina compatível, sem setup entre máquinas | Aprovado |
| US15_CT02 | Ordens compatíveis com mais de uma máquina | Distribuir pela quantidade de ordens, com desempate pelo código | Aprovado |
| US15_CT03 | Ordem sem máquina compatível | Retornar 422, informar a pendência e não salvar a sugestão | Aprovado |
| US15_CT04 | Ordem compatível somente com máquina inativa | Retornar 422, informar a pendência e não salvar a sugestão | Aprovado |

### Evidências

- [US15_CT01](evidencias/us15/US15_CT01.png)
- [US15_CT02](evidencias/us15/US15_CT02.png)
- [US15_CT03](evidencias/us15/US15_CT03.png)
- [US15_CT04](evidencias/us15/US15_CT04.png)

Os identificadores correspondem aos cenários automatizados em `compatibilidade.feature`.
Não foi confirmada a correspondência formal desses IDs com o CT-119 do plano anterior.

## 4. Testes automatizados

| Tipo de teste | Executados | Aprovados | Reprovados |
|---|---:|---:|---:|
| Testes unitários US15 (incluindo integração de regras) | 9 | 9 | 0 |
| Testes de integração US15 | 6 | 6 | 0 |
| Testes de integração US14 após adequação à US15 | 11 | 11 | 0 |
| Cypress US15 | 4 | 4 | 0 |
| Backend — resultado consolidado de execuções complementares | 246 | 246 | 0 |
| Cypress Chrome — regressão direcionada US13, US14 e US15 | 23 | 23 | 0 |

Os testes específicos já fazem parte dos resultados consolidados e não devem
ser somados novamente. A regressão completa do backend não foi repetida após
a última correção dos dados de teste da US14.

### 4.1. Regressão do backend

A primeira regressão da versão integrada executou 244 testes em 229,16 segundos,
com 237 aprovados e sete falhas, todas no arquivo `test_us14_prazos_prioridades.py`.
Os produtos preparados pela versão antiga desse arquivo não possuíam máquinas
compatíveis ativas e a API retornava 422, conforme a nova regra da US15.

O arquivo foi atualizado para associar os produtos a uma máquina ativa,
adaptar a conferência de `maquina_id` e incluir dois novos casos de integração.
A execução direcionada dos 11 testes desse arquivo terminou com todos aprovados
em 14,94 segundos. Os dois testes que já haviam passado nesse arquivo não são
contados duas vezes: 235 aprovados fora dele + 11 aprovados na execução final =
246 testes distintos aprovados em execuções complementares.

Os casos adicionais verificam o sequenciamento independente por máquina,
inclusive a possibilidade de aumento de setup para respeitar a urgência,
e o bloqueio por dados de urgência incompletos em outra máquina.

Não foi gerado um XML único de regressão Pytest após a última correção. Os
números acima registram os resultados observados no terminal local.

### 4.2. Regressão do frontend

A regressão direcionada foi executada em Cypress 16.3.0 e Chrome 158 (headless),
com a seleção `@US13 or @US14 or @US15`.

| Feature | Executados | Aprovados | Reprovados |
|---|---:|---:|---:|
| Compatibilidade de máquinas | 4 | 4 | 0 |
| Prazos e prioridades | 6 | 6 | 0 |
| Sequência sugerida | 13 | 13 | 0 |
| Total | 23 | 23 | 0 |

Tempo total informado pelo runner: 11 minutos e 59 segundos. Os três arquivos
JUnit correspondem à mesma execução; os nomes originais gerados pelo runner
foram preservados.

- [Resumo da regressão integrada](evidencias/us15/chrome-regressao-resumo.json)
- [JUnit 1](evidencias/us15/results-98571cbe6e290813537ff344b262770b.xml)
- [JUnit 2](evidencias/us15/results-a727bd01be666a101e0fd644fdd7afe3.xml)
- [JUnit 3](evidencias/us15/results-c0b95fbbaac9f0a8fc3e2cef89f52271.xml)

Os vídeos e as demais capturas permanecem nos artefatos locais do Cypress,
sem necessidade de versionar as gravações no Git.

### 4.3. Verificações adicionais

| Verificação | Resultado |
|---|---|
| Build do frontend | Aprovado |
| ESLint | Aprovado |
| Alembic upgrade head e current nos dois bancos de teste | Aprovado |
| Git diff --check HEAD antes da documentação | Sem erros de whitespace após correção; aviso LF/CRLF |

## 5. Problemas encontrados e resolvidos

| Problema | Solução ou tratamento | Situação |
|---|---|---|
| Cypress não localizava a máquina na sequência sugerida | Atualização do build do frontend | Resolvido na execução seguinte |
| Timeout intermitente na preparação do banco E2E | Execução isolada do seed bem-sucedida e ajuste do limite local de `cy.task` | Não voltou a ocorrer na regressão integrada; causa exata não identificada |
| Conflitos com a US14 integrada à main | Conciliação da rota e dos steps, mantendo as regras das duas histórias | Resolvido |
| Duas revisões head do Alembic | Migration de união e atualização dos bancos de testes | Resolvido |
| Testes da US14 preparavam produtos sem máquinas compatíveis | Atualização dos dados dos testes e reexecução direcionada | Resolvido |

Nenhum defeito funcional permaneceu identificado nos cenários aprovados.

## 6. Ambiente de testes

- Sistema operacional: Windows.
- Banco de dados: PostgreSQL 18.
- Backend: Python, FastAPI e Pytest.
- Frontend: React, TypeScript e Vite 8.3.5.
- Testes E2E: Cypress 16.3.0, Node.js 24.11.1 e Chrome 158 (headless).
- Banco do Pytest: `setupflow_us15_test`.
- Banco do Cypress: `setupflow_us15_e2e_test`.

Os bancos utilizados são separados do banco de desenvolvimento. As credenciais
locais não fazem parte da documentação nem dos relatórios versionados.

## 7. Definition of Done

| Critério | Situação |
|---|---|
| Implementação da história de usuário | Concluída localmente |
| Testes automatizados escritos e aprovados | Concluído no escopo das execuções locais registradas |
| Validação funcional local | Concluída |
| Evidências Cypress registradas | Concluído |
| Documentação técnica | READMEs e relatório preparados; revisão final pendente |
| Revisão e integração via Pull Request | Pendente |
| Pipeline de CI sem falhas | Pendente |
| Homologação, quando exigida | Pendente de confirmação |
| Aceite do Product Owner | Pendente |

## 8. Conclusão

Os testes demonstraram que a sugestão atribui ordens a máquinas compatíveis
ativas, calcula o setup por máquina e mantém as regras de prazo e prioridade
nos cenários de integração. A ausência de máquina compatível ativa impede a
geração e a persistência da sugestão.

O backend registrou 246 testes distintos aprovados em execuções complementares,
e o Cypress registrou 23 cenários aprovados em uma única regressão direcionada
no Chrome. A implementação está apta a seguir para a revisão de código.
A regressão Cypress de todas as features, a execução no Electron, o CI e o
aceite do PO não foram confirmados nesta entrega local.
