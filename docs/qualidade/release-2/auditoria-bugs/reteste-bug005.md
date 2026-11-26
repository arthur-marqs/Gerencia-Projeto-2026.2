## Reteste de QA — BUG-005

**Resultado — Correção validada localmente.**

- **Issue** — [#31](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31), US01 / Driver06, Release 2 / Sprint 3.
- **Commit testado** — [`8978fc1`](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commit/8978fc110480f363b65873443c072bcc4469cfd6), branch `docs/qualidade`.
- **Data e ambiente** — 26/11/2026, Windows 11 26H2, Chrome 158, Cypress 16.3.0, Vite e FastAPI com PostgreSQL 18.6 isolado. [Manifesto](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/manifesto.json)

**Causa e correção** — A falha na consulta de identidade colocava a interface no estado de login. Agora a tela informa a indisponibilidade e oferece **Tentar novamente**. A área autenticada é liberada após a confirmação da sessão. Um HTTP 401 continua levando ao login. [Código da correção](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/8978fc110480f363b65873443c072bcc4469cfd6/frontend/src/App.tsx#L36-L133)

| Cenário | Resultado | Evidência |
|---|---|---|
| HTTP 503 na abertura com sessão válida | **Aprovado.** O aviso apareceu e o painel ficou indisponível enquanto a identidade não foi confirmada. | [Captura do aviso](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/503-aviso-e-retry.png) |
| Nova consulta com sessão válida | **Aprovado.** HTTP 200 real restaurou o painel sem novo login e sem recarregar. | [Captura do painel](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/200-painel-sem-novo-login.png) |
| Nova consulta após expirar a sessão da fixture | **Aprovado.** HTTP 401 real exibiu o formulário de login e manteve a navegação protegida fora da tela. | [Captura do login](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/401-login.png) |
| HTTP 200 atrasado após 401 de um recurso protegido | **Aprovado.** A resposta atrasada foi descartada e o login permaneceu visível. | [JUnit do reteste integrado](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/reteste-integrado.xml) |

**Regressão** — 17 cenários oficiais de autenticação aprovados, incluindo os cinco novos que falharam antes da correção. Os três retestes integrados também passaram. No ensaio integrado, o 503 inicial e a resposta atrasada foram controlados no navegador. A sessão e as demais respostas foram verificadas na API real. [Antes da correção](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/antes.json) · [Suíte de autenticação](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/autenticacao.json) · [Novos cenários](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/8978fc110480f363b65873443c072bcc4469cfd6/frontend/cypress/e2e/autenticacao/restauracao-sessao.feature)

**US32** — 31 cenários passaram na regressão. O CT35 foi interrompido na preparação da massa por erro de memória do Argon2 e passou no reteste isolado, completando a verificação dos 32 cenários. Lint e build do frontend passaram. [Regressão US32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/usuarios.json) · [Reteste CT35](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/35ec52629a4aacc2f9dd57e3c527750babe298d6/docs/qualidade/release-2/auditoria-bugs/evidencias/reteste-bug005/usuarios-ct35.json)

**Situação da integração** — Aguardando integração à `main`. O parecer se aplica ao reteste local.
