# SetupFlow — Release 2

## Visão geral

A Release 2 amplia o SetupFlow com recursos para configurar tempos de setup, estimar a duração das ordens e apoiar o planejamento da produção. O incremento permite montar planejamentos manualmente, gerar sequências sugeridas considerando as restrições cadastradas, comparar alternativas e aprovar uma sequência para consulta pelo Operador.

Até 26/11/2026, os itens da Release 2 descritos nesta nota estavam integrados à branch `main` e aceitos pelo Product Owner. O estado consolidado do projeto registra 19 histórias de usuário e 5 drivers integrados nas Releases 1 e 2, até o commit `08a62f5`. Consulte o [estado das entregas e o Definition of Done](../../status-projeto.md#release-2) para os itens, pull requests e evidências.

## Funcionalidades incluídas

- **Duração e setup das ordens (US09 e US10):** informar a duração estimada de uma ordem de produção e configurar tempos de setup entre famílias de produtos.
- **Matriz de setup (US11):** consultar os tempos de setup entre famílias, considerando valores direcionais entre uma família de origem e uma família de destino.
- **Compatibilidade entre produtos e máquinas (US26):** cadastrar as compatibilidades utilizadas como restrição no planejamento.
- **Planejamento da produção (US12 a US17):** montar um planejamento manual, gerar uma sequência sugerida, considerar prazos e prioridades, respeitar a compatibilidade entre produtos e máquinas, comparar a sequência manual com a sugerida e aprovar o planejamento.
- **Gerenciamento de usuários (US32):** administrar os usuários do sistema conforme as permissões atribuídas ao perfil autorizado.

## Requisitos de qualidade incluídos

- **Driver01 — Integridade das ordens:** preservar a integridade dos dados durante gravações de ordens de produção.
- **Driver02 — Idempotência:** prevenir a criação de ordens duplicadas quando uma requisição é reenviada.
- **Driver04 — Controle de acesso:** bloquear operações protegidas quando o usuário não possui autenticação ou perfil autorizado.
- **Driver06 — Validade da sessão:** recusar sessões expiradas ou invalidadas.

O Driver05, relacionado à limitação de tentativas repetidas de login, já havia sido entregue na Release 1 e permanece parte da base de qualidade do SetupFlow.

## Verificação

As histórias e os drivers foram integrados por pull requests e possuem registros de validação e aceite na [página de estado das entregas](../../status-projeto.md#release-2), que centraliza os links de implementação e os relatórios de QA.

A execução de integração contínua da `main` associada ao commit `08a62f5` foi concluída com os cinco jobs aprovados. O pipeline contempla testes do backend, lint e build do frontend e testes de aceitação ponta a ponta com Cypress. Consulte a [execução integrada no GitHub Actions](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972).

## Pendências e evolução

- **Homologação:** a implantação da Release 2 em um ambiente de homologação não foi confirmada durante a elaboração desta nota. Portanto, esta documentação não afirma que houve deploy. Quando a implantação for realizada ou localizada, registrar aqui a URL do ambiente, o commit implantado e a evidência da validação/demonstração; até lá, não marcar esse critério do DoD como concluído sem comprovação.
- **Correções em acompanhamento:** o estado do projeto registra que as correções dos BUG-004 (máquina que deixou de ser elegível antes da aprovação) e BUG-005 (recuperação da sessão após falha temporária) foram validadas na branch `docs/qualidade` e ainda aguardavam integração à `main` na atualização de 26/11/2026. Verifique a [auditoria de bugs e os retestes](../../qualidade/release-2/auditoria-bugs/README.md) antes de considerar essas correções parte desta versão.
- **Evolução futura:** registro da execução das ordens, replanejamento, histórico de alterações e indicadores de produção permanecem como evoluções do projeto, conforme a [documentação de arquitetura](../../arquitetura/arquitetura.md#sequenciamento-e-execução).

## Execução local

Consulte o [README principal](../../../README.md), o [guia de configuração do backend](../../../backend/README.md) e o [guia do frontend](../../../frontend/README.MD) para configurar o ambiente, iniciar a aplicação e executar os testes.
