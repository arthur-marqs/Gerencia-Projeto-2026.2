# Registro de evidências — US-32 / SC-66

Roteiro: [testes manuais e automatizados](../../roteiro-testes-us32.md).

Preencha os resultados após executar os testes. A presença deste modelo não
significa que os cenários tenham sido executados ou aprovados.

## Identificação da execução

| Campo | Valor |
| --- | --- |
| Data e horário | A preencher |
| Responsável | A preencher |
| Branch e commit testado | A preencher com `git branch --show-current` e `git rev-parse HEAD` |
| Ambiente / sistema operacional | A preencher |
| Navegadores e versões | A preencher |
| Banco de demonstração | A preencher, sem credenciais |
| Banco dos testes automatizados | A preencher; deve ser separado e terminado em `_test` |
| Ticket | SC-66 |
| Release / Sprint | R2 / Sprint 2 |

## Resultados

Use **Aprovado**, **Reprovado**, **Bloqueado** ou **Não executado**. Substitua
as referências abaixo pelos arquivos efetivamente capturados e informe o que
foi observado. Os nomes completos sugeridos estão no roteiro.

| Teste | Critério / objetivo | Resultado | Evidências e observações |
| --- | --- | --- | --- |
| T01 | C1 — Cadastro ativo e login por perfil | Não executado | A preencher; prefixo `t01` |
| T02 | C2 — Consulta de ativos/inativos sem senha/hash | Não executado | A preencher; prefixo `t02` |
| T03 | C3 — Edição, senha preservada e permissões imediatas | Não executado | A preencher; prefixo `t03` |
| T04 | C4 — Cancelamento e confirmação da exclusão | Não executado | A preencher; prefixo `t04` |
| T05 | C5 — Campos inválidos e preservação dos dados anteriores | Não executado | A preencher; prefixo `t05` |
| T06 | C6 — E-mail duplicado, normalizado e reservado para inativos | Não executado | A preencher; prefixo `t06`; concorrência no T13 |
| T07 | C7 — Desativação, reativação e sessões antigas inválidas | Não executado | A preencher; prefixo `t07` |
| T08 | C8 — Bloqueio por ordens/planejamentos e autoria preservada | Não executado | A preencher; prefixo `t08` |
| T09 | C9 — Proteção do último administrador ativo | Não executado | A preencher; prefixo `t09`; concorrência no T13 |
| T10 | C10 — Menu restrito e respostas 401/403 | Não executado | A preencher; prefixo `t10` |
| T11 | C11 — Troca de senha e invalidação das sessões | Não executado | A preencher; prefixo `t11` |
| T12 | C12 — Primeiro administrador e segunda conta pela interface | Não executado | A preencher; prefixo `t12` e cadastro do T01 |
| T13 | API, regressão da US-32 e quatro casos de concorrência | Não executado | A preencher; prints `t13` e relatórios XML |

## Falhas ou impedimentos

Registre ID do teste, passos realizados, resultado esperado, resultado obtido,
arquivo da captura e referência ao defeito, quando houver.

A preencher após a execução.

## Relatórios automatizados

Após executar os comandos do roteiro, inclua nesta pasta:

- `pytest-us32.xml`: execução completa dos testes da US-32.
- `pytest-us32-concorrencia.xml`: execução dos quatro casos de concorrência.
- `t13a-pytest-us32.png` e `t13b-concorrencia.png`: saída do terminal.

Resultados obtidos nesta execução: **a preencher**.
