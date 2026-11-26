# Auditoria de bugs — SetupFlow Release 2

Avaliação original em 26/11/2026, Sprints 2 e 3, na versão integrada [`08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f).

**Parecer da auditoria original — Pendente de ajustes.** Foram confirmados dois bugs, um de severidade alta e um de severidade média. As correções do BUG-004 e do BUG-005 foram validadas localmente em 26/11/2026 e aguardam integração. [Reteste do BUG-004](reteste-bug004.md) · [Reteste do BUG-005](reteste-bug005.md)

| Ordem sugerida | Achado | Severidade | Prioridade sugerida | Situação | Issue |
|---|---|---|---|---|---|
| 1 | [Aprovação publica sugestão com máquina que deixou de ser elegível](bug-aprovacao-maquina-inelegivel.md) | Alta | Alta | Correção validada nas duas variantes, aguardando integração. [Reteste](reteste-bug004.md) | [#30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) |
| 2 | [Falha temporária ao restaurar sessão deixa a interface na tela de login](bug-restauracao-sessao-indisponivel.md) | Média | Média | Correção validada localmente, aguardando integração. [Reteste](reteste-bug005.md) | [#31](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31) |

O [relatório consolidado](relatorio-validacao.md) reúne escopo, comandos, regressão dos três bugs históricos, critérios de correção e pendências de validação. Os resultados e reproduções estão em [evidências](evidencias/).
