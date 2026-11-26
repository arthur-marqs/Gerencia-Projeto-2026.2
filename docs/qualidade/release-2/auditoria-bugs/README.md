# Auditoria de bugs — SetupFlow Release 2

O [ciclo de regressão de 26/11/2026](../regressao-release-2.md) atualiza a verificação da integração, repete os retestes e registra as novas medições. [Relatório de Qualidade da Release 2](../../../releases/release2/relatorio-qualidade-release-2.md)

Avaliação original em 26/11/2026, Sprints 2 e 3, na versão integrada [`08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f).

As histórias e os drivers integrados foram aceitos pelo PO, com a DoD concluída por item. [Estado das entregas](../../../status-projeto.md)

**Acompanhamento dos defeitos em 26/11/2026.** A auditoria encontrou dois bugs no código integrado. As correções foram validadas em `docs/qualidade` e aguardam integração à `main`. [Reteste do BUG-004](reteste-bug004.md) · [Reteste do BUG-005](reteste-bug005.md)

| Ordem sugerida | Achado | Severidade | Prioridade sugerida | Situação | Issue |
|---|---|---|---|---|---|
| 1 | [Aprovação publica sugestão com máquina que deixou de ser elegível](bug-aprovacao-maquina-inelegivel.md) | Alta | Alta | Correção validada nas duas variantes, aguardando integração. [Reteste](reteste-bug004.md) | [#30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30) |
| 2 | [Falha temporária ao restaurar sessão deixa a interface na tela de login](bug-restauracao-sessao-indisponivel.md) | Média | Média | Correção validada localmente, aguardando integração. [Reteste](reteste-bug005.md) | [#31](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31) |

O [relatório consolidado](relatorio-validacao.md) reúne escopo, comandos, regressão dos três bugs históricos, critérios de correção e pendências de validação. Os resultados e reproduções estão em [evidências](evidencias/).
