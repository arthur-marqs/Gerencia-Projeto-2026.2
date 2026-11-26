## Reteste de QA — BUG-004

**Resultado — Correção validada localmente.**

- **Issue** — [#30](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/30), US17 e US15, Release 2 / Sprint 3.
- **Correção** — [`b6c72f2`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/b6c72f2beb9c4ba92a4c7871547c895574c8afd2), branch `docs/qualidade`.
- **Data e ambiente** — 26/11/2026, Windows 11 26H2, PostgreSQL 18.6 isolado, Chrome 158 e Cypress 16.3.0.
- **Versão retestada** — Alterações locais sobre `7bf75c9`. O código e as suítes correspondem ao commit da correção, conforme a impressão digital da execução. [Manifesto](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/manifesto.json)

| Cenário | Resultado | Evidência |
|---|---|---|
| Máquina desativada após a geração | **Aprovado.** A sugestão saiu da lista de candidatos. O POST com a seleção antiga retornou HTTP 409 e orientou a gerar nova sugestão. | [Captura](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/maquina-inativa.png) |
| Compatibilidade removida após a geração | **Aprovado.** A API retornou HTTP 409, sem gravar aprovação ou itens. | [Captura](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/compatibilidade-removida.png) |
| Alteração de cadastro concorrente | **Aprovado nas duas variantes.** A aprovação aguardou a alteração e foi recusada após a confirmação no banco. | [JUnit da API](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/reteste-api.xml) |
| Sugestão legada e reenvio de aprovação existente | **Aprovado.** A sugestão sem máquina foi recusada e o reenvio da aprovação existente retornou o registro original, sem duplicação. | [Testes de integração](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/b6c72f2beb9c4ba92a4c7871547c895574c8afd2/backend/testes/integration/test_us17_aprovacao.py#L126-L223) |

Nos dois cenários originais, o Operador não recebeu um novo plano para execução e a sugestão continuou disponível para consulta histórica. [JUnit do reteste no Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/reteste-chrome.xml)

**Regressão final** — 331 testes de backend e 12 cenários no Chrome para US15, US16 e US17 aprovados, além dos 2 retestes específicos no navegador. A primeira execução em paralelo registrou erros de memória no Argon2 e um timeout no Chrome. As repetições sequenciais passaram integralmente. [JUnit do backend](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/regressao-backend.xml) · [Regressão no Chrome](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/0476c207a47b776959c0a1d9eb63127d2a4430c8/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug004/regressao-chrome.json)

**Situação da integração** — Aguardando integração à `main`. O parecer se aplica ao reteste local.
