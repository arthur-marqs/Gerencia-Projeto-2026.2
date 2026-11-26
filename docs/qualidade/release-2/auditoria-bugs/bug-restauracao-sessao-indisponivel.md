# [BUG] Falha temporária ao restaurar sessão deixa a interface na tela de login

**Acompanhamento em 26/11/2026** — Registrado na [issue #31 / BUG-005](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/31). Correção validada antes do merge e integrada à `main` em `c43587c`. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) [Relatório de reteste](reteste-bug005.md)

**RELEASE:** R2  
**SPRINT:** 3  
**SEVERIDADE:** Média  
**PRIORIDADE:** Média — sugestão para triagem  
**RESPONSÁVEL:** A definir  
**REPORTADO POR:** A confirmar  
**US RELACIONADA:** US01 — Autenticação, em regressão na R2.  
**DRIVER RELACIONADO:** Driver06 — Sessão expirada ou invalidada.

## DESCRIÇÃO

Ao abrir ou atualizar o SetupFlow com uma sessão válida, uma falha temporária na consulta de identidade leva a interface à tela de login. No ensaio, foi preciso recarregar a página para recuperar a navegação com a mesma sessão.

## AMBIENTE

- **Ambiente:** Local, frontend compilado com Vite, API Uvicorn e PostgreSQL 18.6 dedicado.
- **Navegador / versão:** Chrome 158.0.8127.38, modo headless.
- **Sistema operacional:** Windows 11 26H2, build 26300.
- **Versão / commit / branch:** `08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f`, branch local `docs/qualidade` no mesmo commit de `origin/main`.
- **Alterações locais incluídas:** Nenhuma no produto. O teste avulso simula uma única resposta HTTP 503 no navegador.
- **Pré-condições e dados de teste:** Planejador de fixture, sessão criada com sucesso em `POST /api/auth/login` e mesma sessão mantida durante o ensaio.

## PASSOS PARA REPRODUZIR

1. Prepare o banco local descartável com `python -m scripts.seed_e2e normal` após aplicar as migrações. Autentique-se com a conta de Planejador da massa e confirme que o painel abre.
2. Em nova visita à página com a mesma sessão, simule HTTP 503 somente na primeira chamada `GET /api/auth/me`. Aguarde a tela de login.
3. Remova a interceptação e repita a consulta real `GET /api/auth/me` com a mesma sessão. Confirme HTTP 200. Devolva o foco à aba e observe a tela.
4. Recarregue a página com a API respondendo normalmente, sem preencher o formulário de login.

Para automatizar, inicie o frontend e a API nos endereços locais do guia, use um Chrome descartável com porta de depuração local 9234, uma aba `about:blank` e a variável `QA_AUDIT_FIXTURE_PASSWORD` com a senha da fixture. Execute na raiz `node docs/qualidade/release-2/auditoria-bugs/evidencias/qa-sessao.mjs resultado-sessao.json`.

## RESULTADO ESPERADO

Com uma falha temporária ao consultar identidade, a interface deve informar a indisponibilidade e oferecer nova verificação da sessão. Após confirmar uma sessão ainda válida, deve liberar a navegação sem nova autenticação. Sessões efetivamente rejeitadas continuam sujeitas ao fluxo de login do Driver06.

## RESULTADO OBTIDO

Em 3 de 3 tentativas, o formulário de login permaneceu visível e a navegação seguiu indisponível após o HTTP 200 da consulta real, o evento de foco e dois segundos de observação. Um novo carregamento restaurou a navegação com a mesma sessão nas três tentativas. A API confirmou a sessão com HTTP 200 e nenhuma reautenticação foi necessária.

## EVIDÊNCIAS

- [Amostras e resultados do navegador](evidencias/sessao-identidade-503.json)
- [Script de reprodução](evidencias/qa-sessao.mjs)
- [Código da restauração da sessão no commit avaliado](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/blob/08a62f5d1d164c7ee2cfbb0282aa7f9784baaf8f/frontend/src/App.tsx#L33-L85)
- [Issue histórica #19, com outro gatilho](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/issues/19)
- **Forma de confirmação:** Execução integrada no Chrome com autenticação e API reais e uma resposta de identidade simulada.
- **Limitações:** Ensaio da reação da interface a HTTP 503. Uma queda de infraestrutura real e outros tipos de falha de identidade ficaram fora da reprodução.

## CRITÉRIO DE CORREÇÃO

    Dado que o Planejador ainda tem uma sessão válida
    E que a primeira consulta de identidade ao carregar a página responde HTTP 503
    Quando a consulta voltar a responder HTTP 200 e a identidade for verificada novamente
    Então a interface deve restaurar a área autenticada sem exigir novo login
    E deve solicitar nova autenticação se a API rejeitar efetivamente a sessão com HTTP 401

## CHECKLIST DE ENCERRAMENTO

- [ ] Causa identificada e registrada nos comentários
- [ ] Correção feita via Pull Request que referencia esta issue
- [ ] Teste de regressão criado ou atualizado
- [ ] Correção verificada pelo QA
