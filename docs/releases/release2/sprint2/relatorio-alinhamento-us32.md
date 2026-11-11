# Relatório de alinhamento ao plano — US-32 / SC-66

**Data:** 11/11/2026 · **Release:** R2 · **Sprint:** 2.

Execução automatizada local assistida, com API real e bancos PostgreSQL
temporários. Revisão do QA, aceite do PO e execução remota do GitHub Actions
permanecem pendentes. Os cenários manuais do roteiro não foram marcados como
executados por esta automação.

## Código e ambiente

- Branch: `feature/US32-CRUD-de-usuarios`.
- Base do código: `01e045dc4c2579ba8fc93662344de8e253807708`, **com alterações
  locais** da implementação BDD e do plano. Os resumos registram `dirty: true` e
  o hash das fontes em cada execução; não se trata de um commit limpo já publicado.
- Windows 11, Node `v26.13.0`, Cypress `16.3.0`, preprocessor Cucumber `28.0.1`.
- Chrome `157.0.8103.40` e Electron `150.0.7871.250`, ambos headless.
- Backend: Python 3.11 em contêiner, dependências de `requirements.txt`.
- PostgreSQL 18 temporário; Pytest em `setupflow_test` e Cypress em
  `setupflow_e2e_test`, com migrations aplicadas. Nenhum banco de desenvolvimento
  foi usado na execução.
- Frontend servido pelo build de produção via Vite preview, na porta 5173;
  API FastAPI real na porta 8000, sem respostas simuladas.

## Resultados obtidos

| Verificação | Executados | Aprovados | Falhas | Evidência |
| --- | --- | --- | --- | --- |
| Backend completo | 197 | 197 | 0 | [JUnit Pytest](evidencias/us32/automatizados/pytest-backend.xml) |
| US-32, dentro do backend | 42 | 42 | 0 | Mesmo JUnit; classe `test_us32_usuarios` |
| Proteção da preparação E2E, dentro do backend | 6 | 6 | 0 | Mesmo JUnit; classe `test_seed_e2e` |
| BDD smoke, Chrome | 5 | 5 | 0 | [Resumo](evidencias/us32/automatizados/chrome-smoke-resumo.json) · [JUnit](evidencias/us32/automatizados/chrome-smoke-junit.xml) |
| BDD regressão, Chrome | 32 | 32 | 0 | [Resumo](evidencias/us32/automatizados/chrome-regressao-resumo.json) · [JUnit](evidencias/us32/automatizados/chrome-regressao-junit.xml) |
| BDD regressão, Electron | 32 | 32 | 0 | [Resumo](evidencias/us32/automatizados/electron-regressao-resumo.json) · [JUnit](evidencias/us32/automatizados/electron-regressao-junit.xml) |
| Frontend lint | 1 comando | Aprovado | 0 | `npm run lint` |
| Frontend build | 1 comando | Aprovado | 0 | `npm run build` |

As contagens de US-32 e proteção de fixtures são subconjuntos dos 197 testes,
e não devem ser somadas novamente. Os 32 cenários BDD expandidos correspondem
aos mesmos 12 critérios em cada navegador. O smoke repete 5 desses cenários.
Nenhum caso foi pulado ou ficou pendente nas execuções BDD finais.

Os testes de concorrência entre cadastros e entre os dois últimos administradores
foram executados na suíte Pytest. O resultado desses quatro casos complementa
CT37 e CT40; a interface automatizada não é usada para afirmar simultaneidade
entre transações.

## Rastreabilidade e capturas

| Caso | Critério | Captura selecionada |
| --- | --- | --- |
| CT32 | C1 — Cadastro e login por perfis | [Acesso da nova conta](evidencias/us32/automatizados/ct32-chrome.png) |
| CT33 | C2 — Consulta de ativos/inativos sem senha/hash | [Consulta](evidencias/us32/automatizados/ct33-chrome.png) |
| CT34 | C3 — Edição com senha em branco e novas permissões | [Dados/perfis atualizados](evidencias/us32/automatizados/ct34-chrome.png) |
| CT35 | C4 — Cancelamento e confirmação da exclusão | [Confirmação com nome/e-mail](evidencias/us32/automatizados/ct35-confirmacao-chrome.png) · [Estado final](evidencias/us32/automatizados/ct35-chrome.png) |
| CT36 | C5 — Campos inválidos e edição preservada | [Dados preservados](evidencias/us32/automatizados/ct36-chrome.png) |
| CT37 | C6 — E-mail duplicado em ativos/inativos | [Erro no cadastro](evidencias/us32/automatizados/ct37-chrome.png) |
| CT38 | C7 — Desativação/reativação e sessões | [Conta desativada](evidencias/us32/automatizados/ct38-desativacao-chrome.png) · [Novo login](evidencias/us32/automatizados/ct38-chrome.png) |
| CT39 | C8 — Vínculos e autoria | [Bloqueio por ordem](evidencias/us32/automatizados/ct39-bloqueio-ordem-chrome.png) · [Bloqueio por planejamento](evidencias/us32/automatizados/ct39-bloqueio-planejamento-chrome.png) |
| CT40 | C9 — Último administrador ativo | [Exclusão recusada](evidencias/us32/automatizados/ct40-chrome.png) |
| CT41 | C10 — Sessão e perfil obrigatórios | [Estado sem sessão](evidencias/us32/automatizados/ct41-chrome.png); respostas 401/403 verificadas nos 14 exemplos do JUnit |
| CT42 | C11 — Nova senha e sessões anteriores | [Novo login](evidencias/us32/automatizados/ct42-chrome.png) |
| CT43 | C12 — Script inicial e segunda conta pela tela | [Segunda conta criada](evidencias/us32/automatizados/ct43-chrome.png) |

Os prints mostram estados visuais; os resultados de API, senha, sessões,
persistência e autoria são comprovados pelas asserções dos cenários e pelos
relatórios. As capturas não substituem o resultado dos passos automatizados.

## Relatórios completos e reprodução

Os relatórios completos permanecem nas pastas locais abaixo, ignoradas pelo Git:

- `frontend/artifacts/cypress/chrome/smoke/`.
- `frontend/artifacts/cypress/chrome/regressao/`.
- `frontend/artifacts/cypress/electron/regressao/`.

Cada pasta contém Cucumber JSON/HTML com steps e anexos, JUnit, resumo JSON,
screenshots e vídeo. A regressão de cada navegador gerou 36 capturas, incluindo
as quatro capturas intermediárias. Dezesseis capturas do Chrome foram selecionadas
para a pasta versionada `evidencias/us32/automatizados/`.

O resumo inclui SHA-256 das fontes para identificar alterações locais. As
execuções finais de Chrome e Electron utilizam o mesmo hash de fontes.
As execuções de smoke e regressão são identificadas separadamente por tags e
horário. Para o JUnit foi selecionado o XML mais recente de cada execução,
evitando somar relatórios antigos existentes nas pastas de desenvolvimento.

Para reproduzir, siga o [guia Cypress](../../../../frontend/cypress/README.md).
Para a execução manual, siga o [roteiro de prints](roteiro-testes-us32.md).
O [plano original](../../../qualidade/Plano-de-Teste-SetupFlow.docx) foi preservado
no formato versionado. A inclusão da US-32 no plano fica a cargo do responsável
pelo documento; os resultados técnicos e as evidências permanecem neste relatório.

## CI, defeitos e aceite

O workflow foi ampliado para executar o aceite no Chrome e no Electron a cada
push/PR, publicando relatórios, capturas e vídeos mesmo em falha. A execução
local confirma os cenários, mas **não há uma execução remota deste novo workflow
registrada neste relatório**. Adicionar o link do GitHub Actions após a execução.

Durante a validação da configuração foram corrigidas a herança de
`ELECTRON_RUN_AS_NODE` do terminal e a passagem das tags ao preprocessor do
Cypress 16 por `expose`. Os resultados acima pertencem às execuções finais após
essas correções. Não houve falha nos testes finais; a situação de bugs no Jira
não foi consultada, e não se declara ausência de bugs críticos/altos no projeto.

Pendências de processo: revisão do QA, exploração manual quando aplicável,
vinculação de evidências ao SC-66, execução remota do CI e aceite do PO.
