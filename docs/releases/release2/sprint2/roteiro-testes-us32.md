# Roteiro de testes e evidências — US-32

**SetupFlow · SC-66 · Release 2 · Sprint 2**

Este roteiro orienta a execução manual e a captura dos prints do gerenciamento
de usuários. Os resultados abaixo são **esperados**, e devem ser comparados com
os resultados obtidos. Preencha o [registro da execução](evidencias/us32/README.md)
ao testar; este documento não registra uma nova execução como aprovada.

## 1. Preparação

Use um ambiente local de demonstração, com dados fictícios. Para comprovar a
criação do primeiro administrador, comece em uma instalação sem conta
administrativa. Se já houver contas administrativas na sua instalação, execute
esse cenário em outro banco local, sem remover as contas existentes.

Com o PostgreSQL e o `.env` configurados conforme o
[README do backend](../../../../backend/README.md), abra um PowerShell na raiz:

```powershell
git branch --show-current
git rev-parse HEAD
Set-Location backend
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe current
.\.venv\Scripts\python.exe -m scripts.create_initial_user
```

No script, informe `Administrador Evidências`, `admin.us32@example.com`, os
perfis `ADMINISTRADOR, PLANEJADOR` e uma senha fictícia de pelo menos oito
caracteres. A senha não deve aparecer na captura. Essa etapa já é a primeira
parte do **T12**.

Inicie o backend nesse terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app
```

Em outro terminal, também a partir da raiz:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Abra **http://localhost:5173**, com largura de janela de pelo menos 1280 pixels
para visualizar o menu lateral. Use `localhost` também para acessar a API
(`http://localhost:8000`), mantendo o mesmo domínio dos cookies.

Organize duas sessões independentes:

| Sessão | Exemplo | Uso |
| --- | --- | --- |
| A | Chrome normal | Administrador; mantenha essa sessão disponível |
| B | Edge ou Chrome anônimo | Conta que está sendo testada |

Duas abas normais do mesmo perfil de navegador compartilham o login. Todas as
janelas anônimas de um mesmo perfil também podem compartilhar a mesma sessão.

Cadastre as contas abaixo pela interface conforme forem necessárias. Mantenha
apenas o administrador inicial com `ADMINISTRADOR`, para permitir o T09.

| Conta | E-mail | Perfis iniciais | Uso |
| --- | --- | --- | --- |
| Administrador Evidências | `admin.us32@example.com` | ADMINISTRADOR, PLANEJADOR | Gestão e proteção do último administrador |
| Ana Evidências | `ana@empresa.com` | PLANEJADOR | Cadastro, consulta, edição, senha e situação |
| Conta Exclusão | `excluir.us32@example.com` | OPERADOR | Exclusão sem vínculos |
| Conta Inativa | `inativa.us32@example.com` | OPERADOR | Consulta de inativos e e-mail reservado |
| Autor de Ordem | `autor.ordem.us32@example.com` | PLANEJADOR | Bloqueio por ordem de produção |
| Autor de Planejamento | `autor.plano.us32@example.com` | PLANEJADOR | Bloqueio por planejamento |

Defina senhas fictícias próprias e anote-as fora dos prints. Não cadastre
produção com Ana ou Conta Exclusão: os históricos serão criados com as contas
específicas do T08.

## 2. Organização dos prints

Salve os arquivos em `docs/releases/release2/sprint2/evidencias/us32/`.
Use os nomes sugeridos em cada teste. As letras `a`, `b`, `c` identificam os
passos de um mesmo cenário.

Nos prints da interface, mostre o título da tela, o registro relevante, a
situação/perfis e a mensagem ou confirmação. Nos prints da API, mostre método,
rota, status HTTP e corpo da resposta. O painel **Network/Rede → Response/Resposta**
do DevTools ajuda a capturar esses dados; a aba Headers/Cabeçalhos pode conter
cookies e a aba Payload pode conter a senha enviada.

Use os dados fictícios deste roteiro. Não inclua cookies, tokens, senhas de banco
ou o conteúdo do `.env` nas evidências. Registre data/hora, responsável, ambiente
e commit no arquivo de registro, junto com o resultado de cada teste.

## 3. Apoio para testar a API

Na sessão desejada, abra o DevTools com **F12 → Console**, mantendo o frontend
aberto em `http://localhost:5173`. O código abaixo usa o cookie dessa sessão,
exibe somente o status e a resposta e também funciona após o login expirar:

```javascript
async function apiUS32(metodo, caminho, dados) {
  var resposta = await fetch('http://localhost:8000' + caminho, {
    method: metodo,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...(dados === undefined ? {} : { body: JSON.stringify(dados) }),
  });
  var texto = await resposta.text();
  var corpo = texto ? JSON.parse(texto) : null;
  console.log(metodo, caminho, resposta.status, corpo);
  return { status: resposta.status, corpo };
}
```

Descubra os IDs na sessão A:

```javascript
var listaUS32 = (await apiUS32('GET', '/api/usuarios')).corpo;
console.table(listaUS32.map(u => ({
  id: u.id, nome: u.nome, email: u.email,
  perfis: u.perfis.join(', '), ativo: u.ativo,
})));
var anaUS32 = listaUS32.find(u => u.email === 'ana@empresa.com');
```

Recarregue `listaUS32` e `anaUS32` se os dados forem alterados. Reexecute a
definição de `apiUS32` quando recarregar a página. Os exemplos usam `await` no
nível superior do Console do navegador.

## 4. Execução dos cenários

Execute a preparação e o **T12 primeiro**, criando Ana como a segunda conta.
Depois execute T01 a T11. O T01 aproveita o cadastro de Ana feito no T12.

### T01 — Cadastro com sucesso (cenário 1)

1. Na sessão A, entre como administrador e abra **Usuários → Novo usuário**.
2. Informe `Ana Evidências`, `ana@empresa.com`, uma senha válida e `Planejador`.
3. Clique em **Salvar usuário**.
4. Confira a confirmação, uma única conta na lista e a situação **Ativo**.
5. Na sessão B, faça login com Ana e abra **Produtos**.
6. Confirme que o menu **Usuários** não aparece para Ana.

**Esperado:** conta ativa criada uma única vez; login funciona e as
funcionalidades de planejador são acessíveis.

**Prints:** `t01a-cadastro-ativo.png` e `t01b-login-planejador.png`.
O primeiro print também serve como segunda parte do T12.

### T02 — Consulta sem senha e sem hash (cenário 2)

1. Na sessão A, cadastre Conta Inativa, selecione-a e confirme **Desativar**.
2. Recarregue a tela e confira que a lista contém contas ativas e inativas.
3. Clique no nome de Ana. Confira nome, e-mail, perfis e situação em
   **Dados do usuário**, sem campo de senha.
4. No DevTools, abra a resposta do `GET /api/usuarios/{id}`. Confira que contém
   `id`, `nome`, `email`, `perfis` e `ativo`, sem `senha` ou `senha_hash`.
5. Consulte também Conta Inativa e confirme a situação **Inativo**.

**Esperado:** ativos e inativos podem ser consultados; a API e a interface
omitem senha e hash.

**Prints:** `t02a-lista-ativos-inativos.png`, `t02b-consulta-usuario.png`
e `t02c-api-sem-senha.png`.

### T03 — Edição e permissões na sessão aberta (cenário 3)

1. Deixe Ana autenticada na sessão B. Antes da alteração, execute ali
   `await apiUS32('GET', '/api/produtos')` e registre o status **200**.
2. Na sessão A, selecione Ana e clique em **Editar**.
3. Altere o nome para `Ana Operação`, desmarque `Planejador`, marque `Operador`
   e deixe **Nova senha** em branco. Mantenha `ana@empresa.com` como e-mail.
4. Salve e confira a confirmação e o perfil **OPERADOR**.
5. Sem fazer logout/login na sessão B, repita o `GET /api/produtos`:
   o status deve ser **403**.
6. Execute `await apiUS32('GET', '/api/auth/me')` na sessão B. Deve retornar
   **200**, com apenas `OPERADOR` nos perfis.
7. Faça logout e novo login de Ana usando a mesma senha inicial.

**Esperado:** dados atualizados, senha preservada e permissões de operador
aplicadas na próxima requisição, inclusive com a sessão anterior aberta.
A atualização visual dos menus ocorre ao recuperar o foco ou em até 30 segundos;
a recusa da API é imediata após o salvamento.

**Prints:** `t03a-permissao-anterior-200.png`, `t03b-edicao-operador.png`
e `t03c-sessao-aberta-403.png`. Registre o novo login em `t03d-senha-preservada.png`.

### T04 — Cancelar e confirmar a exclusão sem vínculos (cenário 4)

1. Na sessão A, cadastre Conta Exclusão com perfil `Operador`.
2. Na sessão B, faça login nessa conta para manter uma sessão aberta.
3. Na sessão A, selecione a conta e clique em **Excluir**.
4. Confira nome e e-mail na confirmação e capture o primeiro print.
5. Clique em **Cancelar**, recarregue e consulte a conta novamente.
6. Solicite **Excluir** outra vez e clique em **Confirmar**.
7. Confira a mensagem de sucesso e a remoção da conta da lista.
8. Na sessão B, tente consultar `/api/auth/me`: deve retornar **401**.
9. Tente um novo login com a conta excluída: deve ser recusado.

**Esperado:** cancelar mantém os dados; confirmar exclui a conta e impede acesso.

**Prints:** `t04a-confirmacao-nome-email.png`, `t04b-cancelamento-preserva.png`,
`t04c-exclusao-sucesso.png` e `t04d-conta-excluida-sem-acesso.png`.

### T05 — Validação e edição atômica (cenário 5)

1. Na sessão A, abra **Novo usuário** e tente salvar com nome vazio, e-mail
   inválido, senha com menos de oito caracteres e nenhum perfil marcado.
2. Confira as mensagens em **todos os campos inválidos**.
3. Consulte Ana e registre seu nome, e-mail e perfil atuais.
4. Em **Editar**, tente mudar o nome para `Alteração inválida`, desmarque todos
   os perfis e informe uma nova senha com sete caracteres. Salve.
5. Confira os erros. Clique em **Cancelar edição** e recarregue a consulta:
   os dados anteriores devem permanecer.
6. Para comprovar que a API também rejeita os dados, use no Console da sessão A:

```javascript
await apiUS32('PUT', '/api/usuarios/' + anaUS32.id, {
  nome: 'Alteração que não deve ser salva',
  email: 'ana@empresa.com',
  perfis: ['PERFIL_INEXISTENTE'],
  senha: '',
});
await apiUS32('GET', '/api/usuarios/' + anaUS32.id);
```

**Esperado:** **422** para perfil inexistente; a consulta seguinte mostra os
dados e perfis anteriores. Repita via API com nome só de espaços, e-mail inválido
ou senha curta para capturar a validação do servidor. O formulário limita nome
a 150 e e-mail a 254 caracteres; valores acima disso devem ser enviados pela API
para testar a rejeição no servidor.

**Prints:** `t05a-erros-cadastro.png`, `t05b-erros-edicao.png`,
`t05c-api-perfil-inexistente-422.png` e `t05d-dados-preservados.png`.

### T06 — E-mail duplicado e normalização (cenário 6)

1. Na sessão A, tente cadastrar outra conta com ` ANA@EMPRESA.COM `, incluindo
   os espaços nas extremidades. Use nome, senha e perfil válidos.
2. Confira a mensagem **O e-mail já está em uso.** e a ausência de nova conta.
3. Edite Conta Inativa e tente substituir seu e-mail por `ANA@EMPRESA.COM`.
   A alteração também deve ser rejeitada; cancele e confirme o e-mail anterior.
4. Tente cadastrar uma conta com ` INATIVA.US32@EXAMPLE.COM ` para comprovar
   que o e-mail de uma conta inativa também permanece reservado.
5. Cadastre uma conta fictícia adicional com um e-mail ainda disponível,
   incluindo maiúsculas e espaços. Consulte o resultado salvo em minúsculas,
   sem espaços nas extremidades.

**Esperado:** conflitos retornam **409** na API e não alteram os registros.
A unicidade entre duas solicitações simultâneas será comprovada no T13.

**Prints:** `t06a-email-duplicado-cadastro.png`, `t06b-email-duplicado-edicao.png`,
`t06c-email-inativo-reservado.png` e `t06d-email-normalizado.png`.

### T07 — Desativação, sessões e reativação (cenário 7)

1. Na sessão B, faça um novo login com Ana e confirme `/api/auth/me` = **200**.
2. Na sessão A, selecione Ana, clique em **Desativar** e confirme.
3. Confira a mensagem de sucesso e a situação **Inativo**.
4. Na sessão B, consulte imediatamente `/api/auth/me`: deve retornar **401**.
   Tente novo login; também deve ser recusado.
5. Na sessão A, selecione Ana e confirme **Reativar**.
6. Na sessão B, **antes de fazer novo login**, repita `/api/auth/me`: a sessão
   anterior deve continuar recusada, com **401**.
7. Faça um novo login com Ana. Agora deve funcionar, mantendo seu perfil Operador.

**Esperado:** desativar invalida as sessões; reativar preserva os perfis e permite
somente um novo login, sem recuperar as sessões anteriores.

**Prints:** `t07a-usuario-inativo.png`, `t07b-sessao-invalidada-401.png`,
`t07c-reativado-sessao-antiga-401.png` e `t07d-novo-login-reativado.png`.

### T08 — Exclusão bloqueada por histórico e autoria preservada (cenário 8)

1. Na sessão A, cadastre Autor de Ordem e Autor de Planejamento, ambos com
   perfil `Planejador`.
2. Garanta que exista um produto ativo. Se necessário, cadastre um como
   administrador com perfil Planejador: código `PROD-US32`, nome
   `Produto Evidência US32`, unidade `UN`.
3. Na sessão B, entre como Autor de Ordem. Abra **Ordens de produção** e
   cadastre `OP-US32-HIST`, com esse produto e quantidade `10`.
4. Na sessão A, tente excluir Autor de Ordem. Confira a mensagem que menciona
   **ordens de produção** e a opção **Desativar usuário**.
5. Entre na sessão B como Autor de Planejamento. Em **Planejamento manual**,
   selecione a ordem pendente `OP-US32-HIST`, nomeie o plano `Plano US32 Histórico`
   e clique em **Salvar planejamento**.
6. Na sessão A, tente excluir Autor de Planejamento. Confira a mensagem que
   menciona **planejamentos** e a opção **Desativar usuário**.
7. Antes de desativar as contas, consulte `/api/planejamentos` na sessão A e
   registre `id_planejamento` e `criado_por` do plano. Compare `criado_por` com
   o ID de Autor de Planejamento em `/api/usuarios`.
8. Use **Desativar usuário** nas duas contas e confirme. Consulte novamente o
   planejamento na sessão A: o `criado_por` deve permanecer igual. A ordem também
   deve continuar listada.

**Esperado:** exclusões retornam **409** e identificam o tipo de vínculo;
desativação funciona e preserva os registros e a autoria. A mensagem da conta
criadora da ordem pode citar também operações de ordens de produção, porque
o cadastro registra a operação de idempotência.

A interface e a resposta de ordens não exibem o criador atualmente. Para
comprovar a autoria da ordem, execute somente esta consulta de leitura no banco
de demonstração, antes e depois da desativação:

```sql
SELECT o.codigo, o.criado_por, u.nome, u.email, u.ativo
FROM ordens_producao o
JOIN usuarios u ON u.id_usuario = o.criado_por
WHERE o.codigo = 'OP-US32-HIST';
```

**Prints:** `t08a-bloqueio-ordem.png`, `t08b-bloqueio-planejamento.png`,
`t08c-autoria-antes.png`, `t08d-autoria-depois.png` e
`t08e-ordem-autoria-preservada.png`. Para o antes/depois, mostre o mesmo ID
do plano/ordem e do criador, com a situação da conta alterada.

### T09 — Proteção do último administrador ativo (cenário 9)

Pré-condição: Administrador Evidências é a única conta **ativa** com
`ADMINISTRADOR`. Se esse não for o estado do seu ambiente, execute este teste
em uma instalação de demonstração com essa condição.

1. Na sessão A, selecione a própria conta e tente **Desativar → Confirmar**.
2. Confira a mensagem **É necessário manter pelo menos um administrador ativo.**
3. Tente **Excluir → Confirmar**; a mesma regra deve impedir a operação.
4. Em **Editar**, desmarque `Administrador`, mantenha `Planejador`, deixe a nova
   senha em branco e salve. A operação também deve ser recusada.
5. Cancele a edição e recarregue a consulta. Confirme a conta ativa, o perfil
   administrativo preservado e o menu **Usuários** acessível.

**Esperado:** as três operações retornam **409**, sem perder acesso administrativo.
A proteção com solicitações simultâneas será comprovada no T13.

**Prints:** `t09a-ultimo-admin-desativacao.png`, `t09b-ultimo-admin-exclusao.png`,
`t09c-ultimo-admin-perfil.png` e `t09d-admin-preservado.png`.

### T10 — Gerenciamento sem permissão (cenário 10)

1. Na sessão B, faça login com Ana, que deve estar ativa como Operador.
2. Capture a tela mostrando seus perfis e a ausência do menu **Usuários**.
3. Execute `await apiUS32('GET', '/api/usuarios')`: deve retornar **403**,
   sem lista de usuários.
4. Faça logout e execute a mesma chamada sem fazer novo login: deve retornar
   **401**, sem dados de usuários.
5. A tentativa de cada operação diretamente pela API está coberta no T13.
   Para repetir manualmente, use um ID de conta fictícia e os mesmos corpos
   válidos dos testes anteriores. Mesmo se o ID for conhecido, o acesso deve
   ser recusado antes de expor ou modificar dados.

| Operação | Método e rota | Sem sessão | Operador |
| --- | --- | --- | --- |
| Listar | `GET /api/usuarios` | 401 | 403 |
| Consultar | `GET /api/usuarios/{id}` | 401 | 403 |
| Cadastrar | `POST /api/usuarios` | 401 | 403 |
| Editar | `PUT /api/usuarios/{id}` | 401 | 403 |
| Desativar | `PATCH /api/usuarios/{id}/status`, `{"ativo": false}` | 401 | 403 |
| Reativar | `PATCH /api/usuarios/{id}/status`, `{"ativo": true}` | 401 | 403 |
| Excluir | `DELETE /api/usuarios/{id}` | 401 | 403 |

**Prints:** `t10a-operador-sem-menu.png`, `t10b-api-operador-403.png`
e `t10c-api-sem-sessao-401.png`.

### T11 — Substituição da senha (cenário 11)

1. Na sessão B, entre como Ana com sua senha atual. Mantenha essa sessão aberta.
2. Na sessão A, selecione Ana, clique em **Editar**, informe uma nova senha
   válida em **Nova senha** e salve, mantendo os demais dados/perfis.
3. Capture a mensagem de atualização, com o campo de senha já ausente da consulta.
4. Na sessão B, consulte `/api/auth/me`: a sessão antiga deve retornar **401**.
5. Tente entrar com a senha anterior: o login deve ser recusado.
6. Tente entrar com a senha nova: o login deve funcionar.

**Esperado:** nova senha substitui a anterior e invalida sessões já abertas.

**Prints:** `t11a-senha-atualizada.png`, `t11b-sessao-anterior-401.png`,
`t11c-senha-antiga-recusada.png` e `t11d-senha-nova-aceita.png`.

### T12 — Primeiro administrador em instalação nova (cenário 12)

Execute este cenário no início, durante a preparação.

1. Aplique as migrations e confira a revisão atual, incluindo `f032ad660001`.
2. Sem conta administrativa existente, execute o script inicial e selecione
   `ADMINISTRADOR, PLANEJADOR`, conforme a seção de preparação.
3. Capture a confirmação no terminal. Nenhuma inserção manual no PostgreSQL
   deve ser necessária para criar o perfil ou atribuí-lo à conta.
4. Faça login na sessão A e confira o menu **Usuários**.
5. Cadastre Ana pela interface, seguindo o T01, como segunda conta da instalação.

**Esperado:** instalação preparada por migrations e script; o primeiro
administrador consegue acessar Usuários e cadastrar outra pessoa.

**Prints:** `t12a-migracao-script-inicial.png`, `t12b-primeiro-admin-menu.png`
e o print `t01a-cadastro-ativo.png` como comprovação da segunda conta.

## 5. T13 — Evidência automatizada para API e concorrência

Use um **banco de testes separado, terminado em `_test`**. A suíte limpa e
recria os dados de teste; não a execute contra o banco usado para os prints.
Siga a configuração de `TEST_DATABASE_URL` no README do backend.

Na pasta `backend`, com o ambiente virtual e a variável configurados:

```powershell
New-Item -ItemType Directory -Force -Path ..\docs\releases\release2\sprint2\evidencias\us32
.\.venv\Scripts\python.exe -m pytest -v --junitxml=../docs/releases/release2/sprint2/evidencias/us32/pytest-us32.xml testes/integration/test_us32_usuarios.py
```

Capture o resumo da execução em `t13a-pytest-us32.png`. Na implementação
atual, a suíte contém **42 casos**; registre a contagem obtida na sua execução.
Se algum caso falhar, registre a falha e o resultado em vez de marcar como aprovado.

Para destacar os quatro casos de concorrência, execute também:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=../docs/releases/release2/sprint2/evidencias/us32/pytest-us32-concorrencia.xml testes/integration/test_us32_usuarios.py -k "cadastros_simultaneos or dois_ultimos_admins"
```

Capture os nomes dos quatro casos e seu resultado em `t13b-concorrencia.png`:

- Um cadastro aceito e outro recusado para o mesmo e-mail simultâneo.
- Exclusão simultânea dos dois últimos administradores preservando um deles.
- Desativação simultânea dos dois últimos administradores preservando um deles.
- Remoção simultânea dos perfis administrativos preservando um deles.

Essas evidências complementam T06 e T09. Dois cliques ou prints isolados não
demonstram, por si só, uma disputa entre transações. O XML e a saída desses testes
registram a execução das verificações com PostgreSQL real.

## 6. Conferência antes de anexar ao ticket

A automação BDD equivalente está em `frontend/cypress/e2e/usuarios.feature`,
com casos CT32–CT43, tags de US/release/smoke/regressão e 32 execuções por
navegador. Para executá-la e obter relatórios, capturas e vídeos, siga o
[guia Cypress](../../../../frontend/cypress/README.md). Os resultados desta
revisão ficam no [relatório de alinhamento](relatorio-alinhamento-us32.md).
A execução automatizada não preenche automaticamente os testes manuais abaixo.

- [ ] Data, responsável, ambiente e commit testado preenchidos no registro.
- [ ] T01 a T12 com resultado real e arquivos correspondentes.
- [ ] T13 com saída dos testes e relatórios XML gerados nesta execução.
- [ ] Prints legíveis, com mensagens, contas e estados relevantes.
- [ ] Nenhuma captura contém senhas, tokens ou cookies.
- [ ] Falhas, bloqueios ou cenários não executados identificados no registro.
- [ ] Evidências anexadas ou vinculadas ao ticket SC-66 e à Sprint 2 da Release 2.
