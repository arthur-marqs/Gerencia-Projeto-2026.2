# Revisão de QA — Driver04 | Controle de acesso às operações

## 1. Identificação

| Campo | Registro |
| --- | --- |
| Item | Driver04 — Controle de acesso às operações |
| Release / Sprint | Release 2; sprint a confirmar no planejamento oficial |
| Repositório | arthur-marqs/Gerencia-Projeto-2026.2 |
| Issue | Não informada nesta avaliação. |
| PR / branch | PR ainda não criada. Branch local: `feature/driver04-controle-acesso`. |
| Commit avaliado | Alteração ainda não commitada. Branch criada sobre a `main` atualizada em `65a1d24`. |
| Data | 25/11/2026 |
| Ambiente | Windows, PowerShell, Python do ambiente virtual do backend, Pytest e PostgreSQL local. |
| Banco de testes | `setupflow_test`, confirmado por `TEST_DATABASE_URL`. |

A avaliação considera os critérios fornecidos para o Driver04: verificar identidade e permissão antes da execução de operações protegidas, rejeitar acessos não autorizados, não expor dados protegidos e preservar os dados persistidos.

## 2. Parecer resumido

**Resultado técnico positivo no escopo exercitado.** A suíte específica executou 44 casos, todos aprovados. Foram avaliadas 22 operações protegidas em dois cenários: ausência de sessão e sessão válida de usuário com perfil `OPERADOR`.

As 22 tentativas sem sessão retornaram HTTP `401`. As 22 tentativas autenticadas como operador retornaram HTTP `403`. Em todas as 44 tentativas, a comparação do conteúdo das tabelas inspecionadas antes e depois da requisição não identificou alteração.

A regressão completa do backend também foi aprovada: **317 testes passaram em 304,90 segundos**.

A implementação de autenticação e autorização já existia nas rotas e dependências do sistema. O incremento específico desta tarefa foi a criação de uma suíte de testes dedicada ao Driver04; não houve alteração no código de produção.

O resultado é local e ainda depende de commit, PR, CI, revisão e aceite para concluir a integração da entrega.

## 3. Rastreabilidade dos critérios

| Critério | Verificação | Resultado |
| --- | --- | --- |
| Identificar usuário sem sessão | 22 operações protegidas, sem cookie de sessão | 22/22 retornaram HTTP 401 |
| Identificar usuário autenticado sem permissão | 22 operações protegidas com perfil `OPERADOR` | 22/22 retornaram HTTP 403 |
| Não expor dados protegidos | Comparação exata do corpo das respostas de acesso negado | 44/44 retornaram somente o campo `detail` esperado |
| Preservar os dados | Snapshot das linhas das tabelas inspecionadas antes e depois de cada tentativa | 44/44 comparações sem diferença |
| Meta de pelo menos 20 tentativas | Suíte com 44 casos parametrizados | Atendida no escopo avaliado |

### 3.1. Operações incluídas na suíte

| Categoria | Operações avaliadas | Quantidade |
| --- | --- | ---: |
| Máquinas | GET, POST, PUT, PATCH e DELETE | 5 |
| Famílias | GET e POST | 2 |
| Tempos de setup | GET e POST | 2 |
| Produtos | GET e POST | 2 |
| Ordens de produção | GET lista, GET por ID, POST, PATCH de duração e PUT de prazo/prioridade | 5 |
| Planejamentos | GET lista, GET por ID, POST e PUT | 4 |
| Sugestões de planejamento | POST e GET por ID | 2 |
| **Total** | | **22** |

Cada uma das 22 operações foi testada com os dois estados de acesso, resultando em 44 casos.

### 3.2. Regras de resposta verificadas

| Estado de acesso | Resultado esperado | Resultado observado |
| --- | --- | --- |
| Sem sessão | HTTP 401 — sessão inválida ou expirada | 22/22 |
| Sessão válida, perfil `OPERADOR` | HTTP 403 — acesso não autorizado para este perfil | 22/22 |

A suíte compara o corpo recebido com a mensagem específica esperada para cada situação. Assim, uma resposta de sucesso ou com dados protegidos não satisfaz as asserções.

### 3.3. Integridade dos dados

O teste captura os registros das tabelas identificadas pelo inspetor SQLAlchemy antes da tentativa e repete a leitura depois da resposta HTTP.

O snapshot é realizado depois do login, quando aplicável, para que a criação legítima da sessão não seja confundida com efeito da requisição não autorizada.

Resultado: as 44 comparações foram idênticas. Não foram observadas inserções, exclusões ou atualizações nas linhas das tabelas inspecionadas.

## 4. Revisão estática da proteção

A inspeção do código identificou duas dependências centrais:

- `get_current_user`, em `backend/app/api/deps.py`, verifica a sessão, sua validade, sua expiração e se o usuário está ativo. A ausência de identidade válida resulta em HTTP 401.
- `require_profiles`, no mesmo módulo, consulta os perfis associados ao usuário e verifica se há interseção com os perfis autorizados. A falta de permissão resulta em HTTP 403.

As rotas de máquinas, produtos, famílias, tempos de setup, ordens, planejamentos e sugestões utilizam a verificação de perfil `PLANEJADOR`.

A rota de usuários possui proteção específica para o perfil `ADMINISTRADOR`.

A restrição visual dos menus na interface não foi considerada mecanismo suficiente de segurança. A validação do Driver04 foi realizada diretamente na API, de modo a exercitar o controle no servidor.

Arquivos de referência:
- [Dependências de autenticação e autorização](../../../backend/app/api/deps.py)
- [Rotas de máquinas](../../../backend/app/api/routes/maquinas.py)
- [Rotas de famílias](../../../backend/app/api/routes/families.py)
- [Rotas de tempos de setup](../../../backend/app/api/routes/tempos_setup.py)
- [Rotas de produtos](../../../backend/app/api/routes/produtos.py)
- [Rotas de ordens](../../../backend/app/api/routes/ordens_producao.py)
- [Rotas de planejamento](../../../backend/app/api/routes/planejamentos.py)
- [Rotas de sugestões](../../../backend/app/api/routes/sugestoes_planejamento.py)

## 5. Testes executados

| Nível | Execução | Resultado |
| --- | --- | --- |
| Testes específicos | `pytest testes\integration\drivers\test_driver04_controle_acesso.py -q` | **44 aprovados**, 61,72 s |
| Regressão completa | `pytest testes -q` | **317 aprovados**, 304,90 s |
| Verificação Git | `git diff --check` | Sem problemas de whitespace |

A suíte específica está em:

`backend/testes/integration/drivers/test_driver04_controle_acesso.py`

Os resultados de console foram registrados em:
- [Execução específica do Driver04](evidencias-driver04/pytest-driver04.txt)
- [Regressão completa do backend](evidencias-driver04/pytest-regressao.txt)

As execuções apresentadas foram feitas com `TEST_DATABASE_URL` apontando para `setupflow_test`.

Não foi gerado JUnit XML nessas duas execuções. Os arquivos de evidência preservam os comandos e os resultados observados no terminal.

## 6. Bugs, limitações e pendências

### 6.1. Perfil SUPERVISOR não existente

A especificação do cenário menciona Operador/Supervisor. No código atual, os perfis reconhecidos são `ADMINISTRADOR`, `PLANEJADOR` e `OPERADOR`, conforme `backend/app/schemas/usuario.py`.

Não foi criado um perfil `SUPERVISOR` durante esta tarefa. A suíte utiliza `OPERADOR`, que é o perfil existente correspondente ao cenário de usuário sem permissão de planejamento.

Caso o PO confirme que Supervisor deve ser um perfil independente, será necessário tratar essa decisão como ampliação de escopo, incluindo schema, persistência, provisionamento de perfis, regras de autorização e testes.

### 6.2. Abrangência da suíte

As 22 operações da suíte específica não representam todos os métodos de todas as rotas protegidas do sistema. Outras operações, como associação de produtos e compatibilidade com máquinas, já possuem verificações em testes das respectivas histórias.

Esses testes fazem parte da regressão de 317 casos, mas não foram contabilizados nas 44 tentativas específicas do Driver04.

### 6.3. Integração ainda pendente

| Pendência | Situação | Critério de fechamento |
| --- | --- | --- |
| Commit da implementação de testes | Pendente | Commit exclusivo do Driver04 |
| Pull Request | Pendente | PR criada e vinculada à branch |
| Revisão de código | Pendente | Revisão registrada |
| CI da branch | Pendente | Pipeline concluída com sucesso no commit avaliado |
| Integração na `main` | Pendente | Merge aprovado |
| Aceite do PO | Não verificado | Decisão rastreável |
| Perfil Supervisor | A confirmar | Alinhamento com o requisito oficial |

## 7. Verificação da DoD

| Critério | Estado | Evidência |
| --- | --- | --- |
| Controle de acesso no backend | Atendido no escopo inspecionado | Dependências de autenticação e autorização nas rotas |
| Pelo menos 20 tentativas não autorizadas | Atendido | 44 casos executados |
| 100% das tentativas rejeitadas | Atendido | 44/44 respostas 401 ou 403 |
| Ausência de alteração dos dados | Atendido no escopo inspecionado | 44/44 snapshots sem diferenças |
| Testes escritos e passando | Atendido localmente | 44 testes específicos e 317 na regressão |
| Código revisado via PR | Pendente | PR ainda não criada |
| Pipeline de CI sem falhas | Não verificado | Execução remota ainda pendente |
| Documentação atualizada | Pendente de integração | Relatório preparado nesta branch |
| Homologação, quando exigida | Não verificado | Exigência não confirmada |
| Aceite do PO | Não verificado | Decisão ainda não registrada |

## 8. Reprodutibilidade

Na pasta `backend`, com o ambiente virtual instalado e a variável `TEST_DATABASE_URL` apontando para o banco de testes:

```powershell
.\.venv\Scripts\python.exe -m pytest testes\integration\drivers\test_driver04_controle_acesso.py -q

.\.venv\Scripts\python.exe -m pytest testes -q
```

A fixture de integração prepara e limpa o banco de testes. Não executar esses comandos contra o banco de desenvolvimento ou produção.

## 9. Parecer final

**Critério técnico atendido no escopo testado; integração e aceite pendentes.**

As 44 tentativas não autorizadas foram rejeitadas corretamente, com distinção entre ausência de autenticação (401) e ausência de permissão (403). As comparações do conteúdo das tabelas inspecionadas não identificaram alterações após nenhuma das tentativas.

A regressão completa também foi aprovada, com 317 testes.

A conclusão não representa aceite final da entrega: ainda são necessários commit, PR, revisão, CI e integração. Também permanece a necessidade de confirmar com o PO se o perfil Supervisor deve existir de forma independente.
