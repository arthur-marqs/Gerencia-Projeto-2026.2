# SetupFlow — Release 1

## Visão geral

A Release 1 entrega a base web do SetupFlow para autenticação de usuários e manutenção de dados usados no planejamento da produção. Inclui uma interface React, uma API FastAPI e persistência em PostgreSQL.

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

## Limitações conhecidas

- A geração automática de sequências de produção ainda não está disponível.
- A prevenção de duplicidade no reenvio de ordens (Driver02) não está implementada.
- O histórico de alterações (US30) não está implementado.
- A Release 1 ainda não possui tag Git nem publicação de Release no GitHub.

## Execução local

Consulte o [README principal](../../../README.md), o [guia de configuração do backend](../../../backend/README.md) e o [guia do frontend](../../../frontend/README.md) para configurar o PostgreSQL, instalar dependências, iniciar a aplicação e executar os testes.