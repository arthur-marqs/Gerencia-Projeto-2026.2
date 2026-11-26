# Estado das entregas do SetupFlow

Atualizado em 26/11/2026. As 19 histórias de usuário e os 5 drivers abaixo foram integrados à `main` até o commit `08a62f5` e aceitos pelo Product Owner. A confirmação do PO vale para o incremento de cada item entregue. [Histórico da main](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/commits/main/) · [CI da main](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/45827103972)

## Definition of Done (DoD)

O checklist está concluído para cada item das tabelas. O critério de homologação segue a exigência da respectiva release.

- [x] Código revisado e integrado via Pull Request
- [x] Critérios de aceite atendidos e validados pelo QA
- [x] Testes escritos e passando
- [x] Pipeline de CI sem falhas
- [x] Implantado em ambiente de homologação, quando exigido na release
- [x] Documentação atualizada
- [x] Aceita pelo PO

## Release 1

| Item | Entrega | Integração | Status |
| --- | --- | --- | --- |
| US01 | Realizar login | [PR #1][pr1] | Aprovada e integrada |
| US02 | Acessar funcionalidades conforme o perfil | [PR #2][pr2] | Aprovada e integrada |
| US03 | Cadastrar e gerenciar máquinas | [PR #6][pr6] | Aprovada e integrada |
| US04 | Cadastrar produto | [PR #3][pr3] | Aprovada e integrada |
| US05 | Cadastrar família de produtos | [PR #4][pr4] | Aprovada e integrada |
| US06 | Associar produto a uma família | [PR #5][pr5] | Aprovada e integrada |
| US07 | Cadastrar ordem de produção | [PR #7][pr7] | Aprovada e integrada |
| US08 | Definir prazo e prioridade da ordem de produção | [PR #8][pr8] | Aprovada e integrada |
| Driver05 | Bloquear tentativas repetidas de login | [PR #1][pr1] · [Testes](../backend/testes/integration/drivers/test_driver05_rate_limiting.py) | Aprovado e integrado |

As decisões da primeira sprint estão na [Sprint Review da Release 1](releases/release1/sprint1/review.md). A publicação correspondente é a [v0.1.0](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/releases/tag/v0.1.0).

## Release 2

| Item | Entrega | Integração | Status |
| --- | --- | --- | --- |
| US09 | Informar duração estimada da ordem de produção | [PR #10][pr10] | Aprovada e integrada |
| US10 | Configurar tempos de setup entre famílias | [PR #11][pr11] | Aprovada e integrada |
| US11 | Visualizar matriz de setup | [PR #16][pr16] · [PR #21][pr21] · [QA](releases/release2/sprint3/relatorio-revisao-pr16-us11.md) | Aprovada e integrada |
| US12 | Planejar a produção manualmente | [PR #12][pr12] | Aprovada e integrada |
| US13 | Gerar sequência sugerida de produção | [PR #22][pr22] | Aprovada e integrada |
| US14 | Considerar prazos e prioridades no sequenciamento | [PR #23][pr23] · [QA](qualidade/release-2/revisao-us14.md) | Aprovada e integrada |
| US15 | Considerar compatibilidade entre produtos e máquinas no sequenciamento | [PR #24][pr24] · [QA](qualidade/release-2/revisao-us15.md) | Aprovada e integrada |
| US16 | Comparar a sequência manual com a sugerida | [PR #27][pr27] · [QA](qualidade/release-2/revisao-us16.md) | Aprovada e integrada |
| US17 | Aprovar planejamento de produção | [PR #28][pr28] · [QA](qualidade/release-2/revisao-us17.md) | Aprovada e integrada |
| US26 | Cadastrar compatibilidade entre produtos e máquinas | [PR #9][pr9] | Aprovada e integrada |
| US32 | Gerenciar usuários | [PR #15][pr15] · [Relatório](releases/release2/sprint2/relatorio-alinhamento-us32.md) | Aprovada e integrada |
| Driver01 | Preservar a integridade dos dados na gravação de ordens | [PR #26][pr26] · [QA](qualidade/release-2/revisao-driver01.md) | Aprovado e integrado |
| Driver02 | Prevenir duplicidade no reenvio de ordens | [PR #13][pr13] · [Testes](../backend/testes/integration/drivers/test_driver02_idempotency_ordens.py) | Aprovado e integrado |
| Driver04 | Bloquear operações protegidas para usuários não autorizados | [PR #29][pr29] · [QA](qualidade/release-2/revisao-driver04.md) | Aprovado e integrado |
| Driver06 | Recusar sessões expiradas ou invalidadas | [PR #17][pr17] · [QA](qualidade/release-2/revisao-driver06.md) | Aprovado e integrado |

## Acompanhamento

- O Driver01 cobre cadastro e atualização de campos de planejamento das ordens. A validação de gravações de andamento acompanha a futura implementação da execução. O Driver04 cobre as operações protegidas disponíveis, incluindo a aprovação avaliada na auditoria integrada. [Cobertura dos drivers](qualidade/release-2/auditoria-bugs/relatorio-validacao.md#4-cobertura-funcional-e-dos-drivers)
- As correções do BUG-004 (elegibilidade da máquina na aprovação) e do BUG-005 (recuperação da sessão após falha temporária) passaram nos retestes em `ee2a4a8` e entraram na `main` em `c43587c`. [PR #32](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) · [Auditoria e retestes](qualidade/release-2/auditoria-bugs/README.md)
- O registro de execução das ordens, o replanejamento, o histórico de alterações e os indicadores de produção fazem parte da evolução do projeto. [Arquitetura](arquitetura/arquitetura.md#sequenciamento-e-execução)

[pr1]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/1
[pr2]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/2
[pr3]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/3
[pr4]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/4
[pr5]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/5
[pr6]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/6
[pr7]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/7
[pr8]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/8
[pr9]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/9
[pr10]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/10
[pr11]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/11
[pr12]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/12
[pr13]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/13
[pr15]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/15
[pr16]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/16
[pr17]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/17
[pr21]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/21
[pr22]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/22
[pr23]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/23
[pr24]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/24
[pr26]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/26
[pr27]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/27
[pr28]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/28
[pr29]: https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/29
