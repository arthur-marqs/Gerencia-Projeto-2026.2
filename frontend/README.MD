# SetupFlow

Aplicação em desenvolvimento para planejamento e acompanhamento da produção, com interface em React e API em FastAPI.


## Estado atual

- **Frontend:** aplicação React, TypeScript, Vite e Tailwind CSS, com tela de login e áreas autenticadas para produtos, famílias de produtos, máquinas, ordens de produção, tempos de setup, matriz de setup, planejamentos e usuários.
- **Autenticação:** integração com a API FastAPI, sessões mantidas por cookies e controle de acesso conforme os perfis do usuário.
- **Planejamento:** consulta dos tempos de setup entre famílias de produtos e visualização da matriz de transições direcionais.
- **Sequência sugerida (US13, US14 e US15):** geração a partir das ordens selecionadas, considerando tempos de setup, prazos, prioridades, durações estimadas e máquinas compatíveis ativas, com consulta da sugestão pelo planejamento.
- **Matriz de setup:** apresenta as famílias nas linhas e colunas, com os tempos de transição em minutos. Transições sem configuração são representadas por um traço. A tela permite atualizar os dados consultados.
- **Backend:** API FastAPI com documentação interativa, endpoint de saúde, autenticação e rotas para os módulos da aplicação.
- **Banco de dados:** PostgreSQL para persistência dos dados da aplicação.
- **Testes:** testes automatizados de backend e testes de aceitação Cypress com Gherkin, incluindo os cenários das US11, US13, US14, US15 e US32.


## Requisitos

- Windows com PowerShell
- Node.js 20.19+ ou 22.12+ e npm (requisito do Vite 8; confira com `node --version` e `npm --version`)
- Python 3.11
- Git (opcional, para obter o projeto)

## Versões das ferramentas

Versões registradas no ambiente de desenvolvimento e no CI:

| Ferramenta | Versão |
| --- | --- |
| Python | 3.11 (CI); 3.11.9 no ambiente local usado |
| FastAPI | 0.162.0 |
| Uvicorn | 0.54.0 |
| Node.js e npm | Verifique com `node --version` e `npm --version` |
| Vite | 8.3.5 |
| create-vite | 9.3.1 |
| Tailwind CSS | 4.x |
| Docker Engine | 29.9.2 |
| Docker Desktop | 4.96.3 |
| Docker Compose | 5.6.1 |
| Cliente `psql` | PostgreSQL 18.6 |

As versões exatas das dependências do frontend ficam registradas em `frontend/package-lock.json` e podem ser instaladas com `npm install`.
O número de versão de `psql` identifica o cliente de linha de comando; ele não confirma a versão do servidor PostgreSQL. Docker e PostgreSQL estão instalados no ambiente, mas não são necessários para iniciar a aplicação no estado descrito neste README.

## Estrutura relevante

```text
Gerencia-Projeto-2026.2/
├── backend/
│   ├── app/
│   ├── migrations/
│   ├── testes/
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── public/
    │   └── images/
    │       ├── setupflow-simbolo.png
    │       └── setupflow-wordmark.png
    ├── src/
    └── package.json
```

Os arquivos das logos devem estar em `frontend/public/images/` com esses nomes. No Vite, os caminhos usados no JSX começam em `/images/`, sem incluir `/public`.

## Instalar dependências

Na primeira execução, abra o PowerShell na pasta raiz do projeto.

### Backend

Se o ambiente virtual ainda não existir:

```powershell
Set-Location .\backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se o ambiente virtual já estiver criado e as dependências instaladas, pule essa etapa.

### Frontend

Em outro terminal PowerShell:

```powershell
Set-Location .\frontend
npm install
```

## Executar a aplicação

Inicie o backend em um terminal:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API ficará disponível em:

- API: http://127.0.0.1:8000
- Documentação interativa: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/api/health

Inicie o frontend em outro terminal:

```powershell
Set-Location .\frontend
npm run dev
```

Abra no navegador o endereço apresentado pelo Vite, normalmente http://localhost:5173/.

Execute cada comando a partir da raiz do repositório. Mantenha os dois terminais abertos enquanto usa a aplicação.

## Comportamento da tela de login

A tela permite preencher e-mail e senha. Ao enviar o formulário:

- campos vazios exibem mensagens de validação;
- e-mail em formato inválido exibe uma mensagem;
- o botão de olho alterna a visualização da senha;
- com os campos válidos, o frontend envia `POST /api/auth/login` com cookies habilitados;
- em caso de sucesso, mostra uma saudação com o nome retornado pela API;
- em caso de erro de autenticação ou conexão, mostra a mensagem correspondente.

## Matriz de setup

A matriz de setup permite consultar os tempos necessários para realizar transições entre famílias de produtos.

- As linhas representam as famílias de origem.
- As colunas representam as famílias de destino.
- Os valores são apresentados em minutos.
- As transições sem configuração são representadas por um traço.
- As transições são direcionais: o tempo de A para B pode ser diferente do tempo de B para A.
- Quando não existem configurações cadastradas, a aplicação apresenta uma mensagem informativa e disponibiliza a atualização da matriz.

A consulta utiliza as rotas `GET /api/families` e `GET /api/tempos-setup`, disponíveis para usuários com perfil Planejador de Produção.

Os testes de aceitação da funcionalidade estão documentados em `frontend/cypress/README.md`.

## Gerar e consultar uma sequência sugerida (US13)

Entre com o perfil **Planejador de Produção**. A geração usa ordens pendentes com
produto associado a uma família e a pelo menos uma máquina compatível ativa,
além dos tempos cadastrados nos dois sentidos para cada par de famílias
atribuídas à mesma máquina. O banco precisa estar na revisão atual das
migrations. [Guia do backend](../backend/README.md#us13--sequência-sugerida-de-produção)

1. Abra **Planejamento manual** e selecione as ordens na sequência de referência.
2. Clique em **Gerar sequência sugerida**. Você pode gerar a sugestão antes de preencher o nome ou salvar o planejamento.
3. Confira a ordem sugerida, a máquina atribuída, o setup por posição e o tempo total estimado em minutos.
4. Para consultar novamente, encontre o planejamento com as mesmas ordens em **Planejamentos cadastrados** e clique em **Consultar sugestão**. Para gerar outra sugestão para um planejamento salvo, clique em **Editar** e use **Gerar sequência sugerida**.

A tela informa quando a seleção está vazia, quando um produto está sem família
ou máquina compatível ativa, ou quando falta o tempo de uma troca. A **Matriz de setup** ajuda a localizar as
transições que precisam ser cadastradas em **Tempos de setup**.


## Sequenciamento por prazos e prioridades (US14)

A geração da sequência sugerida também considera os prazos, as prioridades
e as durações estimadas das ordens de produção.

O fluxo de utilização permanece o mesmo da US13:

1. Acesse o **Planejamento manual** com o perfil Planejador de Produção.
2. Selecione as ordens de produção.
3. Clique em **Gerar sequência sugerida**.
4. Confira a sequência apresentada e os tempos de setup.

A sequência sugerida pode apresentar um tempo total de setup superior
ao original quando isso favorece o atendimento aos prazos e prioridades.

Quando houver dados de prazo ou prioridade, todas as ordens selecionadas
devem possuir prazo, prioridade e duração estimada. Caso existam dados
incompletos, a geração é bloqueada e a pendência é informada.

Quando nenhuma ordem possui prazo ou prioridade, o comportamento
de otimização de setup da US13 é mantido, respeitando a distribuição por
máquina da US15.

As regras de sequenciamento estão descritas no
[README do backend](../backend/README.md#us14--prazos-e-prioridades-no-sequenciamento).

Os resultados dos testes estão disponíveis no
[relatório de testes da US14](../docs/releases/release2/sprint3/relatorio-testes-us14.md).


## Compatibilidade de máquinas (US15)

A geração da sequência sugerida considera as máquinas ativas compatíveis
com os produtos das ordens selecionadas.

1. Cadastre as máquinas e associe as compatíveis a cada produto.
2. No **Planejamento manual**, selecione as ordens pendentes.
3. Clique em **Gerar sequência sugerida**.
4. Confira a máquina indicada em cada item, a sequência e os tempos de setup.

Quando existe mais de uma máquina compatível, a distribuição considera a
quantidade de ordens já atribuídas na sugestão, com desempate pelo código da
máquina. O sequenciamento por prazo, prioridade e setup ocorre separadamente
em cada máquina. Não há setup entre máquinas diferentes.

Se algum produto não possui máquina compatível ativa, a tela informa a
ordem e o produto com pendência e nenhuma sugestão é salva. Após corrigir
as associações, é possível solicitar a geração novamente.

A máquina atribuída também fica registrada nas sugestões consultadas.
Sugestões anteriores à US15 podem aparecer com **Máquina não atribuída**.

Consulte as [regras do backend](../backend/README.md#us15--compatibilidade-entre-produtos-e-máquinas-no-sequenciamento)
e o [relatório de testes da US15](../docs/releases/release2/sprint3/relatorio-testes-us15.md).

## Banco de dados

O login real depende do PostgreSQL e da configuração do backend descrita no [README do backend](../backend/README.md). Para usar o formulário no navegador, inicie o PostgreSQL e a API antes de iniciar o frontend. Os testes automatizados do backend não precisam dos servidores HTTP do frontend ou do Uvicorn; usam `TestClient` e um PostgreSQL de teste.

Para uma visão das pastas, arquivos e do fluxo de autenticação, consulte o [mapa visual do projeto](../docs/estrutura-projeto.md).

## Encerrar

Pressione `Ctrl+C` em cada terminal para encerrar o servidor Vite e o Uvicorn.
