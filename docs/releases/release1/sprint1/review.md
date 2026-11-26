# Sprint Review das US - Feita pelo PO — Sprint 1

Esta ata registra a decisão da Sprint 1 em 29/10/2026. Os nove itens aceitos na sprint estão integrados e com o DoD concluído. A US09 e o Driver02 foram integrados e aceitos na Release 2. [Estado das entregas](../../../status-projeto.md)

## Sprint Goal definido na Planning
Permitir que o usuário entre no sistema, cadastre os dados essenciais e registre ordens prontas para serem planejadas.

## Resultado demonstrado
- **Acesso e permissões:** login e controle das funcionalidades conforme o perfil do usuário (US01 e US02).
- **Cadastros essenciais:** gerenciamento de máquinas, cadastro de produtos e famílias e associação entre produtos e famílias (US03 a US06).
- **Ordens de produção:** cadastro de ordens com prazo e prioridade definidos (US07 e US08).
- **Proteção de login:** prevenção contra tentativas repetidas de autenticação (Driver05).
- O repositório contém telas do frontend e rotas da API para esses fluxos, além de testes de integração para as histórias US01 a US08 e para o Driver05.
- **Itens que avançaram para a Sprint 2.** Informar a duração estimada da ordem (US09) e prevenir duplicidade no reenvio de ordens (Driver02).

## Avaliação do PO
- Meta atingida? Parcialmente
- Comentário: o usuário pode entrar no sistema, acessar funcionalidades conforme seu perfil, cadastrar os dados essenciais e registrar ordens com prazo e prioridade. A meta não foi totalmente atingida porque a duração estimada da ordem ainda estava em andamento. A prevenção de duplicidade no reenvio também ficou pendente. Dos 11 itens da sprint, 9 foram concluídos e 2 não.

## Decisões do PO — Sprint 1

### US01 — Realizar login
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o fluxo de autenticação e criação de sessão possui testes de integração.
- Evidências: [SC-5](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-5) · [testes de autenticação](../../../../backend/testes/integration/test_us01_auth.py)
- Data: 29/10/2026

### US02 — Acessar funcionalidades conforme o perfil
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o controle de acesso por perfil possui testes de integração.
- Evidências: [SC-19](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-19) · [testes de controle de acesso](../../../../backend/testes/integration/test_us02_access_control.py)
- Data: 29/10/2026

### US03 — Cadastrar e gerenciar máquinas
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o cadastro e gerenciamento de máquinas possuem testes de integração.
- Evidências: [SC-20](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-20) · [testes de máquinas](../../../../backend/testes/integration/test_us03_maquinas.py)
- Data: 29/10/2026

### US04 — Cadastrar produto
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o cadastro de produtos possui testes de integração.
- Evidências: [SC-21](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-21) · [testes de produtos](../../../../backend/testes/integration/test_us04_produtos.py)
- Data: 29/10/2026

### US05 — Cadastrar família de produtos
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o cadastro de famílias de produtos possui testes de integração.
- Evidências: [SC-22](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-22) · [testes de famílias](../../../../backend/testes/integration/test_us05_families.py)
- Data: 29/10/2026

### US06 — Associar produto a uma família
- Resultado: **Aprovada**
- Justificativa: User Story concluído; a associação entre produtos e famílias possui testes de integração.
- Evidências: [SC-23](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-23) · [testes de associação produto-família](../../../../backend/testes/integration/test_us06_produto_familia.py)
- Data: 29/10/2026

### US07 — Cadastrar ordem de produção
- Resultado: **Aprovada**
- Justificativa: User Story concluído; o cadastro de ordens de produção possui testes de integração.
- Evidências: [SC-24](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-24) · [testes de ordens de produção](../../../../backend/testes/integration/test_us07_ordens_producao.py)
- Data: 29/10/2026

### US08 — Definir prazo e prioridade da ordem de produção
- Resultado: **Aprovada**
- Justificativa: User Story concluído; a definição de prazo e prioridade possui testes de integração.
- Evidências: [SC-25](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-25) · [testes de prazo e prioridade](../../../../backend/testes/integration/test_us08_prazo_prioridade_ordem.py)
- Data: 29/10/2026

### US09 — Informar duração estimada da ordem de produção
- Resultado na Sprint 1: **Reprovada**
- Justificativa: história ainda por iniciar na data da review.
- Situação atual: **Aprovada e integrada na Release 2**. [SC-26](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-26) · [PR #10](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/10) · [Testes de duração estimada](../../../../backend/testes/integration/test_us09_duracao_estimada.py)


### Driver02 — Prevenção de duplicidade no reenvio de ordens
- Resultado na Sprint 1: **Reprovado**
- Justificativa: implementação em aberto na data da review.
- Situação atual: **Aprovado e integrado na Release 2**. [SC-55](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-55) · [PR #13](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/13) · [Testes do Driver02](../../../../backend/testes/integration/drivers/test_driver02_idempotency_ordens.py)
- Data: 29/10/2026

### Driver05 — Proteção contra tentativas repetidas de login
- Resultado: **Aprovado**
- Justificativa: driver concluído; a proteção contra tentativas repetidas possui testes de integração específicos.
- Evidências: [SC-56](https://gerencia-team-arthur-leo-luiz.atlassian.net/browse/SC-56) · [testes do Driver05](../../../../backend/testes/integration/drivers/test_driver05_rate_limiting.py)
- Data: 29/10/2026


> As evidências de teste são os arquivos existentes no repositório; as suítes não foram executadas durante o preenchimento deste review.
