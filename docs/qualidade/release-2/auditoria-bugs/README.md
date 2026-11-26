# Auditoria de bugs — SetupFlow Release 2

O [ciclo de regressão de 26/11/2026](../regressao-release-2.md) atualiza a verificação da integração, repete os retestes e registra as novas medições. [Relatório de Qualidade da Release 2](../../../releases/release2/relatorio-qualidade-release-2.md)

Avaliação original em 26/11/2026, Sprints 2 e 3, na versão integrada [`08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f).

As histórias e os drivers integrados foram aceitos pelo PO, com a DoD concluída por item. [Estado das entregas](../../../status-projeto.md)

**Integração em 26/11/2026.** Os BUG-004 e BUG-005 foram reproduzidos no commit `08a62f5`. As correções passaram nos retestes em `ee2a4a8` e foram integradas à `main` em `c43587c`. As issues #30 e #31 estão fechadas. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32)

| Ordem sugerida | Achado | Severidade | Prioridade sugerida | Situação | Issue |
|---|---|---|---|---|---|
| 1 | [Aprovação publica sugestão com máquina que deixou de ser elegível](bug-aprovacao-maquina-inelegivel.md) | Alta | Alta | Integrada em `c43587c`. Reteste pré-merge aprovado nas duas variantes. [Reteste](reteste-bug004.md) | [#30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) |
| 2 | [Falha temporária ao restaurar sessão deixa a interface na tela de login](bug-restauracao-sessao-indisponivel.md) | Média | Média | Integrada em `c43587c`. Reteste pré-merge aprovado. [Reteste](reteste-bug005.md) | [#31](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31) |

O [relatório consolidado](relatorio-validacao.md) reúne escopo, comandos, regressão dos três bugs históricos, critérios de correção e pendências de validação. Os resultados e reproduções estão em [evidências](evidencias/).
