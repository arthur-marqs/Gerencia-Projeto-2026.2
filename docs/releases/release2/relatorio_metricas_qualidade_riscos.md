# Relatório de Métricas de Qualidade e Riscos — Release 2

## 1. Identificação

SetupFlow · Sprints 2 e 3 · 26/11/2026 · QA responsável: Leonardo Istamilo. A regressão local foi executada em `08a62f5`, os retestes em `ee2a4a8` e a CI do merge e o ensaio de carga em `c43587c`. O [relatório de qualidade][qualidade] reúne escopo, ambiente, bugs e DoD.

## 2. Consolidação das métricas

O fechamento informou atendimento das nove metas. A coluna **Fechamento informado** preserva os valores declarados pela equipe. A coluna **Evidência verificada** indica o alcance da auditoria. O [plano versionado][plano] registra Q-07 na coluna da Release 2 e define Q-06 pelo estado do pipeline no fechamento. A taxa histórica de Q-06 pertence ao plano informado para o fechamento.

| ID | Métrica e meta | Fechamento informado | Evidência verificada |
| --- | --- | --- | --- |
| Q-01 | Execução · 100% dos casos das US entregues | 100% | **85,42%** (41/48 IDs) no recorte de regressão. Sete bloqueados. O total do plano integral ficou **Não levantado**. [Casos][regressao] |
| Q-02 | Aprovação · ≥ 95% dos casos executados | 100% | **100%** dos IDs concluídos (41/41). Quatro reprovações em ensaios complementares pré-merge. A taxa global ficou **Não levantada**. [Contagens][resultados] |
| Q-03 | Bugs críticos ou altos abertos · 0 no fechamento | 0 | Zero entre as cinco issues do GitHub consultadas após o merge (1 alta e 4 médias, todas fechadas). O total no Jira ficou **Não levantado**. [Bugs][bugs] |
| Q-04 | US com critério definido antes da sprint · 100% | 100% | Critérios exercitados no recorte. A versão histórica da DoR e a data dos critérios de cada US no Jira ficaram **Não verificadas**. [Revisão US14][us14] |
| Q-05 | PRs com revisão antes do merge · 100% | 100% | **25%** (4/16 PRs de entrega) com revisão formal publicada antes do merge. Os outros 12 ficaram sem confirmação documental. [DoD e PRs][dod] |
| Q-06 | Execuções verdes na `main` · ≥ 90% no período | 92% | **5/5 jobs** aprovados no merge `c43587c`. A execução atende ao critério de pipeline do plano versionado. O numerador e o denominador dos 92% ficaram **Não levantados**. [CI do merge][ci] |
| Q-07 | Tempo de resposta · p95 ≤ 2 s por operação | Atendido | **Atendido no ensaio local**. Maior p95 de **1.083,27 ms**, na consulta de ordens com 10 VUs em `c43587c`. [Ensaio e resultados][carga] |
| Q-08 | Perfis com teste de negação de acesso · 100% | 100% | **3/3 perfis exercitados** e **2/3 com negativa explícita verificada** (Planejador e Operador). Administrador foi exercitado na gestão de contas. **100% de negação por perfil ficou sem confirmação**. [Testes da US32][usuarios] · [Driver04][driver04] |
| Q-09 | Fluxos principais com tratamento de erro · 100% | 100% | BUG-004 e BUG-005 reproduzidos em `08a62f5`, retestados com sucesso em `ee2a4a8` e integrados em `c43587c`. O inventário completo de fluxos e a taxa global ficaram **Não levantados**. [Bugs][bugs] |

**Base de cálculo.** Execução = (aprovados + reprovados) ÷ planejados × 100. Aprovação = aprovados ÷ (aprovados + reprovados) × 100. Denominador zero resulta em **Não se aplica**. Os resultados por ferramenta, navegador, versão e tentativa de medição estão no [registro de regressão][regressao].

## 3. Avaliação dos riscos da release

Pontuação original da [matriz de riscos][matriz] = (6 − P) × S. P vai de 1 (muito provável) a 5 (muito improvável), e S de 1 (leve) a 5 (maior). A matriz registra dois riscos vermelhos (R-01, R-05) e sete amarelos. A equipe ainda não registrou uma reavaliação de P e S residuais.

| Risco | P / S originais | Pontos | Evidência e situação | Responsável |
| --- | --- | ---: | --- | --- |
| R-01 · Tentativas excessivas de login | 3 / 5 | 15 | **Validado no recorte.** Driver05 (Release 1) revalidado em 20 ciclos, com 200 tentativas adicionais bloqueadas. [Regressão][regressao] | Leonardo |
| R-02 · Sessão válida após logout ou revogação | 3 / 3 | 9 | **Validado no recorte.** 20 sessões expiradas e 20 invalidadas recusadas. Os 20 GETs com token desconhecido também receberam 401. Máximo HTTP de **30,743 ms** entre as condições. A suíte US32 exercitou invalidação após mudança da conta. [Drivers][drivers] · [US32][usuarios] | Arthur |
| R-03 · Autorização parcial | 3 / 4 | 12 | **Validação parcial.** Driver04 registrou **28/28 acessos negados** sem exposição ou alteração dos dados e 14/14 controles positivos. Replanejamento ficou fora da matriz e a negativa do Administrador ficou sem comprovação em Q-08. [Drivers][drivers] | Luiz |
| R-04 · Duplicidade de ordens | 3 / 4 | 12 | **Validado no recorte.** Driver02 registrou 20 operações e 100 reenvios sem duplicidades. A janela de 24 h foi verificada com relógio controlado. [Drivers][drivers] | Leonardo |
| R-05 · Sequenciamento com dados incompletos | 2 / 4 | 16 | **Validado no recorte.** US14 confirmou prazo e prioridade, comparou a sequência em cenário pequeno e registrou recusa de dados insuficientes (422). O CT-115 passou após decisão do PO. [Regra e reteste][us14] · [Casos][regressao] | Arthur |
| R-06 · Perda de alterações concorrentes | 3 / 4 | 12 | **Validação parcial.** Driver01 comprovou rollback em 20 interrupções. A evidência é de integridade transacional sob interrupção. O risco específico de atualizações simultâneas sobre a mesma ordem requer evidência própria. [Drivers][drivers] | Luiz |
| R-07 · Lentidão na consulta do aprovado | 3 / 3 | 9 | **Protocolo do risco pendente.** Q-07 mediu p95 de **590,21 ms** na consulta de aprovados com 10 VUs. A matriz exige 30 VUs, 10.000 ordens, plano de 500, páginas de 50, gerador externo, ≥ 1.000 consultas, p95 ≤ 2 s, p99 ≤ 3 s e erros ≤ 1%. [Q-07][carga] · [Matriz][matriz] | Leonardo |
| R-08 · Lentidão em listagens e indicadores | 3 / 2 | 6 | **Validação parcial.** A listagem de ordens foi medida em Q-07 (p95 de 1.083,27 ms com 10 VUs). A evolução do histórico e os indicadores não foram exercitados nesse ensaio. [Q-07][carga] | Arthur |
| R-09 · Lentidão na geração da sugestão | 3 / 3 | 9 | **Validação parcial.** Q-07 mediu geração com quatro ordens (p95 de 661,63 ms com 10 VUs). As amostras de 10, 20, 50 e 100 ordens previstas na matriz ficaram pendentes. [Q-07][carga] · [Matriz][matriz] | Luiz |

## 4. Pendências de verificação

| Pendência | Evidência necessária | Responsável |
| --- | --- | --- |
| Cobertura global de Q-01, Q-02, Q-03, Q-04 e Q-09 | Inventário do plano de casos e fluxos, histórico do Jira e registro da DoR antes das plannings | QA e PO |
| Q-05, Q-06 e Q-08 | Revisões para o restante dos PRs, série de execuções da `main` com período e contagens, e caso negativo do Administrador | SM, DevOps e QA |
| CT-119 e homologação | Decisão sobre a política do lote misto e confirmação da exigência de homologação para esta entrega | PO e DevOps |
| R-06 a R-09 | Evidência de concorrência e execução dos protocolos de desempenho da matriz | Desenvolvimento, QA e DevOps |

## 5. Parecer do QA

**Validação integral inconclusiva para `c43587c`.** O SHA integrado tem CI verde, correções retestadas no mesmo conteúdo de código e Q-07 atendida no cenário local. O parecer mantém as lacunas de cobertura, desempenho e homologação registradas acima. O aceite do PO para as entregas consta do [estado do projeto][estado]. [Parecer e evidências][parecer]

## 6. Histórico de revisão

| Revisão | Data | Registro |
| --- | --- | --- |
| 1.0 | 26/11/2026 | Consolidação inicial de métricas e riscos por Leonardo Istamilo. |
| 1.1 | 26/11/2026 | Inclusão dos valores de fechamento informados. |
| 1.2 | 26/11/2026 | Revisão por Codex das fontes, medições, riscos e parecer. |

[qualidade]: relatorio-qualidade-release-2.md
[resultados]: relatorio-qualidade-release-2.md#b-resultado-do-ciclo-final-de-regressão
[drivers]: relatorio-qualidade-release-2.md#6-validação-dos-drivers
[bugs]: relatorio-qualidade-release-2.md#7-bugs-encontrados-e-corrigidos
[dod]: relatorio-qualidade-release-2.md#8-verificação-da-dod
[carga]: relatorio-qualidade-release-2.md#q-07--teste-de-carga-e-tempo-de-resposta
[parecer]: relatorio-qualidade-release-2.md#11-parecer-do-qa
[plano]: ../../qualidade/Plano-de-Qualidade-SetupFlow.xlsx
[matriz]: ../../qualidade/GP-RiscoBaseadoDefeitos-SetupFlow.xlsx
[regressao]: ../../qualidade/release-2/regressao-release-2.md
[us14]: ../../qualidade/release-2/revisao-us14.md#reavaliação-após-a-decisão-do-po
[usuarios]: ../../../backend/testes/integration/test_us32_usuarios.py
[driver04]: ../../qualidade/release-2/revisao-driver04.md
[estado]: ../../status-projeto.md#release-2
[ci]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45882475010
