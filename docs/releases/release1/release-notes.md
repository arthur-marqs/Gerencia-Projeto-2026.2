# SetupFlow — Release 1

## Visão geral

A Release 1 entrega a base web do SetupFlow para autenticação de usuários e manutenção de dados usados no planejamento da produção. Inclui uma interface React, uma API FastAPI e persistência em PostgreSQL.

A publicação da Release 1 está na tag [v0.1.0](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/releases/tag/v0.1.0). As histórias US01 a US08 e o Driver05 foram aprovados pelo PO e integrados. [Entregas e Definition of Done](../../status-projeto.md#release-1)

## Funcionalidades incluídas

- **Autenticação e sessão:** login, validação de credenciais, sessão persistida, consulta do usuário autenticado e logout.
- **Proteção de login:** registro de falhas e bloqueio temporário após tentativas inválidas repetidas.
- **Controle de acesso:** operações protegidas conforme o perfil do usuário, incluindo restrição de recursos de cadastro ao Planejador de Produção.
- **Máquinas:** cadastro, consulta, edição, ativação, inativação e exclusão quando não há registros relacionados.
- **Produtos e famílias:** cadastro e consulta, incluindo associação e remoção da associação entre produto e família.
- **Ordens de produção:** cadastro e consulta, com definição e atualização de prazo e prioridade.
- **Interface web:** telas de login, máquinas, produtos, famílias e ordens de produção integradas à API.

## Verificação

A integração contínua executa os testes do backend e as verificações de lint e build de produção do frontend. A [execução da pipeline da Release 1](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/actions/runs/40959460641) foi concluída com sucesso. Consulte o [relatório da pipeline](relatorio_pipeline.md) para os detalhes e a evidência JUnit.

## Evolução após a Release 1

- A geração automática de sequências (US13) e a prevenção de duplicidade no reenvio de ordens (Driver02) foram integradas e aceitas na Release 2.
- O histórico de alterações (US30) segue previsto no escopo de evolução. [Estado das entregas](../../status-projeto.md)

## Execução local

Consulte o [README principal](../../../README.md), o [guia de configuração do backend](../../../backend/README.md) e o [guia do frontend](../../../frontend/README.MD) para configurar o PostgreSQL, instalar dependências, iniciar a aplicação e executar os testes.
