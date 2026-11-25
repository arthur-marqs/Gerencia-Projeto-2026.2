# Backend do SetupFlow

Este guia explica como configurar o backend e o PostgreSQL em uma máquina de desenvolvimento.

Cada pessoa executa sua própria instância local do PostgreSQL. O GitHub contém as migrations que recriam a estrutura do banco, mas não contém o banco local, usuários de teste, sessões ou senhas.



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
a geração exige um tempo para cada sentido dos pares de famílias selecionadas.
A heurística agrupa ordens da mesma família e testa um caminho a partir de cada
família, escolhendo a próxima troca de menor custo. Empates na escolha da próxima
família seguem a primeira ocorrência na seleção. Quando não há dados de prazo ou prioridade nas ordens selecionadas,
a ordem original é mantida se nenhuma alternativa avaliada reduz
o tempo total de setup. Como a busca é gulosa, outras
sequências podem ter custo menor que o da sugestão encontrada.

Com A → B de 20 minutos e B → A de 30 minutos, a seleção A, B, A tem setup
total de 50 minutos. A sugestão A, A, B reduz o total para 20 minutos.

A resposta traz `id_sugestao`, `criado_por`, `criado_em`,
`tempo_setup_original_minutos`, `tempo_setup_total_minutos` e `itens` em ordem
sugerida. Cada item traz `ordem_id`, `posicao`, `posicao_original` e `setup_minutos`.
A geração pode ocorrer antes de criar um planejamento. A consulta pelo
planejamento localiza a sugestão pelo conjunto de ordens, independentemente da
posição em que elas foram gravadas no planejamento manual. Esses dados ficam
disponíveis para a comparação da US16.

A API retorna 422 para seleção vazia ou duplicada, ordens fora do status pendente,
produtos sem família ou tempos de troca ausentes. A mensagem identifica a ordem e
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

Vínculos de autoria em ordens, planejamentos, sugestões de planejamento e
operações de cadastro de ordens bloqueiam a exclusão da conta. A API retorna 409
com os tipos de vínculo e a indicação `pode_desativar`. A interface oferece a
desativação quando permitida e a autoria continua registrada.
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

O cadastro de ordens (`POST /api/ordens-producao`) exige o cabeçalho `Idempotency-Key` com um UUID. A chave é única por usuário e fica registrada junto com a ordem; seu reconhecimento não expira, portanto permanece válido por pelo menos 24 horas. Reenvios com a mesma chave e conteúdo retornam a ordem original com HTTP 200; reutilizar a chave com conteúdo diferente retorna HTTP 409. Use uma nova chave para uma operação distinta e um novo `codigo` de ordem, que continua único.

Execute a suíte do Driver02, que verifica 20 operações cujo commit é confirmado mas cuja resposta é perdida, cinco reenvios por operação, conflito de conteúdo, operações distintas, concorrência, retenção e recuperação após falha antes da confirmação:

```powershell
.\.venv\Scripts\python.exe -m pytest -v testes\integration\drivers\test_driver02_idempotency_ordens.py
```

As duas suítes também podem ser executadas juntas com `.\.venv\Scripts\python.exe -m pytest -v --junitxml=junit.xml testes`.


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
