# Backend do SetupFlow

Este guia explica como configurar o backend e o PostgreSQL em uma máquina de desenvolvimento.

Cada pessoa executa sua própria instância local do PostgreSQL. O GitHub contém as migrations que recriam a estrutura do banco, mas não contém o banco local, usuários de teste, sessões ou senhas.

As rotas integradas abrangem autenticação e usuários, cadastros de produção, ordens, tempos de setup e planejamento manual, sugerido, comparado e aprovado. [Estado das entregas e DoD](../docs/status-projeto.md) · [Arquitetura](../docs/arquitetura/arquitetura.md)


## Ferramentas usadas

- Python 3.11
- PostgreSQL 18 (também usado no CI)
- FastAPI
- SQLAlchemy
- Alembic
- Psycopg 3

## Pré-requisitos

- Python instalado
- PostgreSQL instalado e em execução
- Git
- Windows PowerShell

## 1. Criar um usuário e um banco locais

Abra o PowerShell e conecte-se ao PostgreSQL com uma conta administradora:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres
```

No prompt do `psql`, crie o usuário da aplicação:

```sql
CREATE ROLE setupflow_dev
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;
```

Defina uma senha para esse usuário. O `psql` solicitará a senha sem exibi-la:

```text
\password setupflow_dev
```

Crie o banco de desenvolvimento:

```sql
CREATE DATABASE setupflow_dev
    OWNER setupflow_dev
    ENCODING 'UTF8';
```

Saia do `psql`:

```text
\q
```

A senha é local de cada desenvolvedor. Não a inclua em arquivos versionados nem a compartilhe no repositório.

## 2. Configurar o ambiente do backend

Na raiz do repositório, entre na pasta do backend e crie o ambiente virtual:

```powershell
Set-Location backend
py -3.11 -m venv .venv
```

Instale as dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crie seu arquivo local `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite `backend/.env` e informe a senha que você definiu para `setupflow_dev`. A configuração deve conter os parâmetros usados pelo backend, por exemplo:

```dotenv
DB_USER=setupflow_dev
DB_PASSWORD=sua_senha_local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=setupflow_dev
SESSION_TTL_HOURS=8
COOKIE_SECURE=false
```

O arquivo `.env` contém credenciais locais e não deve ser enviado ao Git. O arquivo `.env.example` deve conter apenas valores de exemplo.

## 3. Criar as tabelas

Com o ambiente configurado, aplique as migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

As migrations criam as tabelas, constraints e índices que declaram e inserem os perfis iniciais. Há um índice declarado no ORM que a migration inicial não cria; consulte o [documento do modelo de dados](../docs/arquitetura/modelo-de-dados.md) para essa diferença.

Para conferir a revisão aplicada:

```powershell
.\.venv\Scripts\alembic.exe current
```

Para conferir as tabelas, conecte-se ao banco da aplicação:

```powershell
psql -h localhost -p 5432 -U setupflow_dev -d setupflow_dev
```

No `psql`, liste as tabelas:

```text
\dt
```

As migrations também criam `produtos` e `maquinas`. O perfil `PLANEJADOR` pode cadastrar e consultar produtos em `/api/produtos` e gerenciar máquinas em `/api/maquinas`; o perfil `OPERADOR` não tem acesso a essas rotas. Máquinas são cadastradas com código e nome obrigatórios, descrição opcional e status ativo por padrão. O cadastro de máquinas também permite editar os dados (`PUT /api/maquinas/{id}`), alterar o status (`PATCH /api/maquinas/{id}/status`) e excluir (`DELETE /api/maquinas/{id}`). A exclusão é bloqueada quando uma chave estrangeira indica registros vinculados; nesses casos, a máquina pode ser inativada para preservar os dados.

Os testes de cadastro e controle de acesso das máquinas ficam em `testes/integration/test_us03_maquinas.py`. Configure `TEST_DATABASE_URL` como descrito acima e execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us03_maquinas.py
```
## 4. Criar um usuário local de teste

O banco começa sem usuários. Crie um usuário pelo script da aplicação:

```powershell
.\.venv\Scripts\python.exe -m scripts.create_initial_user
```

Siga as solicitações do script. Para a primeira conta administrativa, selecione
`ADMINISTRADOR`. É possível acumular perfis informando, por exemplo,
`ADMINISTRADOR, PLANEJADOR`. O perfil administrativo permite gerenciar usuários;
as funcionalidades de produção continuam exigindo `PLANEJADOR` ou `OPERADOR`
conforme as permissões de cada recurso. A senha deve ter pelo menos oito
caracteres e será armazenada como hash. A migration da US-32 disponibiliza
`ADMINISTRADOR`, sem inserção manual no PostgreSQL.

## US13 — Sequência sugerida de produção

Aplique `alembic upgrade head` na pasta `backend` para incluir a revisão
`13e41f6d48c2`. As rotas usam o cookie de sessão e exigem o perfil `PLANEJADOR`.

| Método | Rota | Operação |
| --- | --- | --- |
| POST | `/api/planejamentos/sugestoes` | Gerar e salvar uma sugestão a partir de `ordens_ids` na ordem de seleção (201) |
| GET | `/api/planejamentos/sugestoes/{id_sugestao}` | Recuperar pelo identificador da sugestão |
| GET | `/api/planejamentos/{id_planejamento}/sugestao` | Recuperar a sugestão mais recente para o conjunto exato de ordens do planejamento |

O cálculo soma os tempos das trocas consecutivas. A primeira ordem e as trocas
dentro da mesma família têm setup de zero minuto. Entre famílias distintas,
a geração exige um tempo para cada sentido dos pares de famílias atribuídas à
mesma máquina (US15).
A heurística agrupa ordens da mesma família e testa um caminho a partir de cada
família, escolhendo a próxima troca de menor custo. Empates na escolha da próxima
família seguem a primeira ocorrência na seleção. Quando não há dados de prazo ou prioridade nas ordens selecionadas,
a ordem original de cada máquina é mantida se nenhuma alternativa avaliada reduz
o tempo total de setup. Como a busca é gulosa, outras
sequências podem ter custo menor que o da sugestão encontrada.

Com A → B de 20 minutos e B → A de 30 minutos, a seleção A, B, A tem setup
total de 50 minutos. A sugestão A, A, B reduz o total para 20 minutos.

A resposta traz `id_sugestao`, `criado_por`, `criado_em`,
`tempo_setup_original_minutos`, `tempo_setup_total_minutos` e `itens` em ordem
sugerida. Cada item traz `ordem_id`, `maquina_id` (US15), `posicao`, `posicao_original`
e `setup_minutos`.
A geração pode ocorrer antes de criar um planejamento. A consulta pelo
planejamento localiza a sugestão pelo conjunto de ordens, independentemente da
posição em que elas foram gravadas no planejamento manual. Esses dados ficam
disponíveis para a comparação da US16.

A API retorna 422 para seleção vazia ou duplicada, ordens fora do status pendente,
produtos sem família, produtos sem máquina compatível ativa (US15) ou tempos de
troca ausentes. A mensagem identifica a ordem e
o produto sem família ou o sentido da troca pendente. Ordens inexistentes e
consultas sem resultado retornam 404. Requisições sem sessão válida retornam 401,
e perfis sem acesso retornam 403. Os registros de uma sugestão são gravados na
mesma transação após a validação dos dados.

Os cenários de aceite da API podem ser executados com `TEST_DATABASE_URL`
apontando para um PostgreSQL isolado cujo nome termine em `_test`.

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us13_sequencia_sugerida.py
```


## US14 — Prazos e prioridades no sequenciamento

A US14 complementa a sequência sugerida da US13, considerando os prazos,
as prioridades e as durações estimadas das ordens de produção, além dos
tempos de setup entre famílias.

A geração continua utilizando a rota `POST /api/planejamentos/sugestoes`,
com acesso restrito ao perfil `PLANEJADOR`.

### Regras de sequenciamento

- São avaliadas alternativas de sequência considerando setup, prazo,
  prioridade e folga até o prazo.
- A previsão de conclusão de cada ordem considera sua duração estimada
  e os tempos de setup acumulados.
- A sequência de referência segue Alta, Média e Baixa. Dentro da mesma
  prioridade, vem primeiro o prazo mais próximo. Com prazos iguais,
  o menor setup total desempata as alternativas avaliadas.
- Uma ordem de prioridade menor só pode passar à frente quando isso evita
  seu atraso e preserva, individualmente, o resultado das ordens mais
  prioritárias. Entre as alternativas válidas, o algoritmo compara a
  quantidade de atrasos por prioridade e o setup total.
- O setup sugerido pode aumentar para respeitar prazo ou prioridade.
- Quando nenhuma ordem selecionada possui prazo ou prioridade, o
  comportamento da US13 é preservado.
- Quando existem dados de prazo ou prioridade, todas as ordens selecionadas
  devem possuir prazo, prioridade e duração estimada para gerar a sugestão.

O cálculo considera o prazo até o final do dia, no fuso `America/Recife`,
e assume produção contínua, sem considerar turnos ou pausas.

A solução utiliza uma heurística de comparação de alternativas e não
garante a obtenção da sequência globalmente ótima.

### Banco de dados

A migration `6b14a2e9c703` remove a restrição que impedia o tempo total de
setup sugerido de superar o tempo original. Os dois valores continuam
sujeitos à restrição de não negatividade.

Execute `alembic upgrade head` para atualizar o esquema.

O downgrade para a revisão anterior pode falhar caso existam sugestões
com tempo de setup superior ao original, pois a restrição anterior não
permite esses registros.

### Testes automatizados

Com `TEST_DATABASE_URL` apontando para um banco exclusivo de testes,
execute na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes/unit/test_us14_sequenciamento.py testes/integration/test_us14_prazos_prioridades.py
```

Os testes verificam o sequenciamento por prazo e prioridade, a possibilidade
de aumento de setup, as validações dos dados e a integração com a API.

Os resultados estão registrados no
[relatório de testes da US14](../docs/releases/release2/sprint3/relatorio-testes-us14.md).


## US15 — Compatibilidade entre produtos e máquinas no sequenciamento

A US15 complementa as US13 e US14 na rota `POST /api/planejamentos/sugestoes`.
A geração continua restrita ao perfil `PLANEJADOR`.

### Regras de distribuição e sequenciamento

- Cada ordem é atribuída somente a uma máquina ativa cadastrada como compatível
  com seu produto. As associações são gerenciadas em
  `PUT /api/produtos/{id}/maquinas`.
- Quando existe mais de uma máquina compatível, a distribuição escolhe a que
  recebeu menos ordens na sugestão em geração. O código da máquina desempata.
  Se essa distribuição exigir um setup sem cadastro, o sistema procura outra
  distribuição entre máquinas compatíveis ativas antes de rejeitar a sugestão.
- Se uma ordem não possui máquina compatível ativa, a API retorna 422,
  identifica a ordem e o produto e não grava nenhuma parte da sugestão.
- Cada máquina tem sua própria sequência, com setup zero na primeira ordem e
  sem contabilizar trocas entre máquinas diferentes. Os tempos direcionais
  exigidos são os das famílias atribuídas à mesma máquina.
- As regras de prazo, prioridade e duração da US14 são aplicadas dentro de
  cada máquina, considerando o mesmo horário inicial. Se qualquer ordem
  possui prazo ou prioridade, os dados de urgência de todas as ordens
  selecionadas são validados antes da geração.
- Os totais original e sugerido são somas dos setups de cada máquina, mantendo
  a mesma distribuição nas duas alternativas. A posição original corresponde
  à ordem de seleção; os itens sugeridos são agrupados por máquina.

A distribuição por quantidade de ordens é uma heurística simples. Ela não
balanceia a carga pela duração das ordens, não considera capacidade ou turnos
e não garante uma solução globalmente ótima.

### Banco de dados

A migration `7c15a3e9d204` adiciona `maquina_id` aos itens de sugestão,
com chave estrangeira para `maquinas`. O campo é opcional para preservar
sugestões anteriores à US15. Novas sugestões registram a máquina atribuída,
que permanece no histórico mesmo que a compatibilidade do produto seja alterada.

A migration de união `b872837156bd` referencia as revisões da US14
(`6b14a2e9c703`) e da US15 (`7c15a3e9d204`). Execute `alembic upgrade head`
para atualizar o banco e `alembic current` para verificar a revisão aplicada.

### Testes automatizados

Com `TEST_DATABASE_URL` apontando para um PostgreSQL exclusivo terminado
em `_test`, execute na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes/unit/test_us15_sequenciamento.py testes/integration/test_us15_compatibilidade.py testes/integration/test_us14_prazos_prioridades.py
```

Os testes cobrem a atribuição e distribuição de máquinas, o bloqueio por
incompatibilidade ou inatividade, os setups independentes, a persistência e a
integração com as regras da US14. Os resultados locais estão no
[relatório de testes da US15](../docs/releases/release2/sprint3/relatorio-testes-us15.md).

## US16 — Comparação de sequências

Em **Planejamento manual**, use **Comparar sequências** no cartão de um
planejamento salvo. A comparação exibe as duas sequências, as mudanças de
posição das ordens e a diferença de setup estimado. Se faltar uma sugestão,
abra o planejamento em **Editar** e use **Gerar sequência sugerida**.

`GET /api/planejamentos/{id_planejamento}/comparacao` é restrita ao perfil
`PLANEJADOR`. A consulta usa a sugestão mais recente para o mesmo conjunto
de ordens e retorna `planejamento`, `sugestao` e `setup` sem gravar dados.
A API retorna 404 se o planejamento não existe ou se ainda não há sugestão
para suas ordens. Cada situação tem uma mensagem própria.

Os totais comparam as duas sequências usando a distribuição por máquina da
sugestão. `diferenca_minutos` é o total sugerido menos o manual. Quando a
ordem manual coincide com a seleção original, a resposta usa os tempos
registrados na geração. Se a ordem manual mudou, recalcula ambos os totais
com os cadastros atuais. Quando falta uma família ou um tempo de troca
necessário ao recálculo, `setup` é `null` e as duas sequências continuam
disponíveis.

## US17 — Aprovar planejamento de produção

Em **Execução da produção**, o Planejador pode selecionar e conferir uma
sequência manual salva ou uma sugestão gerada antes de aprová-la. Na mesma
tela, Planejador e Operador podem consultar as sequências aprovadas.

| API | Perfil | Comportamento |
| --- | --- | --- |
| `GET /api/planejamentos/aprovacoes/candidatos` | `PLANEJADOR` | Lista sequências com ordens pendentes e disponíveis para aprovação. |
| `POST /api/planejamentos/aprovacoes` | `PLANEJADOR` | Aprova a origem `manual` ou `sugerida` identificada por `origem_id`. A interface envia `ordens_ids` na ordem conferida para detectar uma edição concorrente. |
| `GET /api/planejamentos/aprovacoes` | `PLANEJADOR`, `OPERADOR` | Lista os planejamentos aprovados com suas ordens, posições e máquinas atribuídas. |

A aprovação guarda a origem escolhida, o responsável, a data e a sequência
de ordens e máquinas em uma transação. A sequência manual pode ter itens
sem máquina atribuída. As alternativas permanecem cadastradas e o manual
aprovado fica protegido contra edição. A mesma ordem só pode integrar uma
aprovação. Reenviar a aprovação da mesma origem retorna o registro existente.
A tentativa sem planejamento retorna 404 com uma mensagem específica.

A versão integrada filtra os candidatos e revalida as atribuições na transação da aprovação. Se uma máquina ficar inativa, perder o vínculo com o produto ou faltar em um item legado, uma nova aprovação retorna HTTP 409 e orienta a gerar outra sugestão. A sugestão original permanece disponível para consulta. [Integração do BUG-004](https://github.com/arthur-marqs/Gerencia-Projeto-2026.2/pull/32) · [Reteste do BUG-004](../docs/qualidade/release-2/auditoria-bugs/reteste-bug004.md)

Aplique `alembic upgrade head` para incluir as tabelas da revisão
`8d17b4f2c306`.
Os testes da API estão em `testes/integration/test_us17_aprovacao.py` e os
casos CT-123 a CT-125 estão no [guia do Cypress](../frontend/cypress/README.md#cenários-da-us17).

## US-32 — Gerenciamento de usuários

Para testar pela interface e organizar os prints dos critérios de aceite, siga o
[roteiro de testes e evidências da US-32](../docs/releases/release2/sprint2/roteiro-testes-us32.md).

O aceite automatizado em Gherkin/Cypress, com Chrome e Electron, está descrito
em [frontend/cypress/README.md](../frontend/cypress/README.md). Ele usa um banco
exclusivo terminado em `_e2e_test`, diferente do banco Pytest e do banco de
desenvolvimento. O [relatório de execução da US-32](../docs/releases/release2/sprint2/relatorio-alinhamento-us32.md)
registra os casos CT32–CT43 e distingue os resultados locais da execução no CI.

Após executar `alembic upgrade head` e criar a primeira conta com o script acima,
faça login e abra **Usuários**. Esse menu aparece apenas para administradores.
A tela lista contas ativas e inativas, consulta detalhes, cadastra e edita nome,
e-mail e múltiplos perfis, e permite desativar, reativar ou excluir com confirmação.
Deixar **Nova senha** em branco preserva a senha atual. A consulta nunca carrega
a senha ou seu hash.

As rotas usam o cookie de sessão da US01 e exigem `ADMINISTRADOR`:

| Método | Rota | Operação |
| --- | --- | --- |
| GET | `/api/usuarios` | Listar contas ativas e inativas |
| GET | `/api/usuarios/{id}` | Consultar uma conta |
| POST | `/api/usuarios` | Criar conta ativa (201) |
| PUT | `/api/usuarios/{id}` | Substituir dados e perfis |
| PATCH | `/api/usuarios/{id}/status` | Alterar situação com `{"ativo": false}` ou `true` |
| DELETE | `/api/usuarios/{id}` | Excluir conta sem vínculos (204) |

POST e PUT recebem `nome`, `email`, `perfis` (lista de códigos) e `senha`.
No PUT, `senha` pode ser omitida, `null` ou `""` para manter a atual.
POST exige senha de pelo menos oito caracteres. Nome e e-mail são aparados;
o nome aceita 1–150 caracteres e o e-mail válido aceita até 254 caracteres,
é armazenado em minúsculas e é único inclusive para contas inativas.

As regras propostas na história foram adotadas conforme seus critérios de aceite:
trocar a senha ou desativar invalida todas as sessões; reativar exige novo login;
alterar perfis tem efeito na próxima requisição mesmo com sessão aberta.
A interface também atualiza a sessão ao recuperar o foco e a cada 30 segundos.
Excluir, desativar ou remover o perfil administrativo do último administrador
ativo retorna 409. Alterações administrativas usam um bloqueio transacional
compartilhado no PostgreSQL, com nova conferência de autorização após a espera,
para preservar essa regra entre solicitações simultâneas. A unicidade do e-mail
também é garantida por constraint do banco. O login bloqueia a conta durante a
criação da sessão para coordená-la com trocas de senha e desativações.

Vínculos de autoria em ordens, planejamentos, sugestões, aprovações de
planejamento e operações de cadastro de ordens bloqueiam a exclusão da conta.
A API retorna 409 com os tipos de vínculo e a indicação `pode_desativar`.
A interface oferece a desativação quando permitida e a autoria continua registrada.
Dados inválidos retornam 422, e-mail em uso retorna 409, conta inexistente retorna
404, sessão ausente/inválida retorna 401 e perfil insuficiente retorna 403.
Nenhuma resposta de gerenciamento, incluindo erros de validação, retorna a senha
informada ou seu hash.

Com `TEST_DATABASE_URL` apontando para um PostgreSQL isolado terminado em `_test`,
execute na pasta `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us32_usuarios.py
```

Os testes cobrem os critérios de API, o script inicial e a concorrência entre
cadastros e entre os dois últimos administradores. A suíte Cypress também cobre
a confirmação e o cancelamento da exclusão pela interface. Os resultados e as
capturas estão no [registro de evidências da US-32](../docs/releases/release2/sprint2/evidencias/us32/README.md).

## 5. Iniciar o backend

Na pasta `backend`, execute:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app
```

Deixe o terminal aberto enquanto estiver usando a aplicação.

- Documentação da API: <http://127.0.0.1:8000/docs>
- Verificação de saúde: <http://127.0.0.1:8000/api/health>

Para encerrar o servidor, pressione `Ctrl+C`.

## 6. Iniciar o frontend

Abra outro terminal do PowerShell, volte à raiz do repositório e entre na pasta do frontend:

```powershell
Set-Location ..\frontend
npm install
npm run dev
```

Abra o endereço informado pelo Vite, normalmente <http://localhost:5173>.

O backend e o frontend precisam permanecer rodando em terminais separados.

## Testes de integração da US01

Os testes exercitam a API e um PostgreSQL real. Crie um banco exclusivo para testes com nome terminado em `_test`, por exemplo `setupflow_test`, usando uma conta administradora:

```sql
CREATE DATABASE setupflow_test
    OWNER setupflow_dev
    ENCODING 'UTF8';
```

Na pasta `backend`, configure `TEST_DATABASE_URL` no PowerShell com as credenciais locais do PostgreSQL:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://setupflow_dev:<SENHA>@localhost:5432/setupflow_test"
```

Se a senha tiver caracteres especiais, use a forma percent-encoded na URL. Os testes exigem essa variável e recusam a execução se o nome do banco não terminar em `_test`. Eles aplicam as migrations antes de limpar e preparar os dados isolados de cada caso. Não defina `DATABASE_URL` para executar a suíte; essa variável não é usada como fallback.

Instale as dependências do backend, incluindo pytest e httpx2 (usado pelo TestClient da versão atual do Starlette):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Execute a suíte básica de login e sessão:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\test_us01_auth.py
```

Execute separadamente a suíte quantitativa do Driver05, que inclui 20 ciclos (200 solicitações bloqueadas) e valida isolamento e limites de tempo:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit-driver05.xml testes\integration\drivers\test_driver05_rate_limiting.py
```

## Idempotência no cadastro de ordens (Driver02)

O cadastro de ordens (`POST /api/ordens-producao`) exige o cabeçalho `Idempotency-Key` com um UUID. A chave é única por usuário e fica registrada junto com a ordem. A implementação mantém o reconhecimento da chave, inclusive após a janela mínima de 24 horas. Reenvios com a mesma chave e conteúdo retornam a ordem original com HTTP 200. Reutilizar a chave com conteúdo diferente retorna HTTP 409. Use uma nova chave e um novo `codigo` para cadastrar outra ordem.

Execute a suíte do Driver02, que verifica 20 operações cujo commit é confirmado mas cuja resposta é perdida, cinco reenvios por operação, conflito de conteúdo, operações distintas, concorrência, retenção e recuperação após falha antes da confirmação:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\drivers\test_driver02_idempotency_ordens.py
```

## Integridade da gravação de ordens (Driver01)

O tratamento de falhas de persistência cobre três operações permitidas ao perfil `PLANEJADOR`.

| Método e rota | Gravação |
| --- | --- |
| `POST /api/ordens-producao` | Cadastro da ordem e da operação vinculada à `Idempotency-Key`. |
| `PATCH /api/ordens-producao/{ordem_id}/duracao-estimada` | Atualização da duração estimada. |
| `PUT /api/ordens-producao/{id_ordem}` | Atualização do prazo e da prioridade. |

Diante de um erro de comunicação detectado durante essas gravações, a API tenta desfazer a transação e retorna HTTP `503` com orientação para atualizar a consulta. Consulte o estado persistido antes de reenviar. Ao repetir o mesmo cadastro com os mesmos dados, mantenha a `Idempotency-Key` da primeira tentativa.

Na pasta `backend`, configure `TEST_DATABASE_URL` para um banco PostgreSQL descartável com nome terminado em `_test`. Execute os 20 testes do driver com o comando abaixo. A suíte injeta exceções no SQLAlchemy após escritas reais e verifica por nova conexão que não ficaram ordens, chaves ou alterações parciais.

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\drivers\test_driver01_integridade_ordens.py
```

O aceite do Driver01 abrange as três gravações disponíveis. A cobertura dos cenários CT-127, CT-128 e CT-129 para início e conclusão de ordens acompanha a futura implementação do registro de execução. [Relatório de QA do Driver01](../docs/qualidade/release-2/revisao-driver01.md)

## Autorização e validade de sessão (Driver04 e Driver06)

Operações protegidas exigem sessão válida. A API retorna HTTP 401 para sessão ausente, expirada ou invalidada e HTTP 403 quando os perfis da sessão não autorizam a operação. A matriz integrada abrange cadastros, planejamento e aprovação. Os testes verificam a rejeição sem alterações no banco, a expiração e a invalidação. [Matriz de QA do Driver04](../docs/qualidade/release-2/revisao-driver04.md) · [Validação do Driver06](../docs/qualidade/release-2/revisao-driver06.md)

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes/integration/drivers/test_driver04_controle_acesso.py testes/integration/drivers/test_driver06_session_expiration.py
```


## Cobertura dos testes do backend

O projeto utiliza `pytest-cov` para medir a cobertura dos testes de integração do backend.

Antes de executar, instale as dependências e configure a variável `TEST_DATABASE_URL` com um banco PostgreSQL exclusivo para testes, conforme explicado anteriormente.

Na pasta `backend`, execute:

```powershell
.\.venv\Scripts\python.exe -m pytest testes/integration -q --cov=app --cov-report=term-missing
```

O comando executa os testes de integração e apresenta no terminal o percentual de cobertura de cada arquivo e a cobertura total.

Para gerar o relatório HTML após a execução:

```powershell
.\.venv\Scripts\python.exe -m coverage html
```

Abra o arquivo `backend/htmlcov/index.html` no navegador para visualizar os resultados e identificar as linhas que não foram executadas.

Na medição realizada em 10/11/2026, foram aprovados 149 testes de integração, com 94% de cobertura do backend.

Os arquivos `.coverage` e a pasta `htmlcov/` são gerados localmente e não devem ser enviados ao repositório.


## Desenvolvimento em equipe

Cada colega deve:

1. Criar seu próprio usuário PostgreSQL e banco local.
2. Criar seu arquivo `backend/.env` usando `.env.example` como referência.
3. Instalar as dependências.
4. Executar `alembic upgrade head`.
5. Criar seu próprio usuário de teste.

As migrations mantêm os esquemas dos bancos locais alinhados. Elas não compartilham os dados inseridos no banco de outra pessoa.
