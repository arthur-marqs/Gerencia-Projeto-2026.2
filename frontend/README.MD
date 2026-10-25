# SetupFlow

Aplicação em desenvolvimento para planejamento e acompanhamento da produção. Esta versão contém a interface inicial de login em React e uma API em FastAPI com endpoint de saúde.

## Estado atual

- **Frontend:** tela de login em React, TypeScript, Vite e Tailwind CSS.
- **Validação:** verifica e-mail e senha no navegador e mostra mensagens para campos inválidos ou vazios.
- **Senha:** botão de olho para mostrar ou ocultar o conteúdo digitado.
- **Marca:** símbolo SetupFlow na coluna esquerda e wordmark no cartão de login.
- **Backend:** API FastAPI com documentação interativa, endpoint `GET /api/health` e rotas de autenticação.
- **Autenticação e banco:** o formulário envia credenciais para a API; o backend verifica a senha e mantém sessões no PostgreSQL.

## Requisitos

- Windows com PowerShell
- Node.js e npm (confira as versões instaladas com `node --version` e `npm --version`)
- Python 3.11.9
- Git (opcional, para obter o projeto)

## Versões das ferramentas

Versões informadas no ambiente usado durante o desenvolvimento:

| Ferramenta | Versão |
| --- | --- |
| Python | 3.11.9 |
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
│   │   └── main.py
│   ├── requirements.txt
│   └── .venv/
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

## Banco de dados

O login real depende do PostgreSQL e da configuração do backend descrita no [README do backend](../backend/README.md). Para usar o formulário no navegador, inicie o PostgreSQL e a API antes de iniciar o frontend. Os testes automatizados do backend não precisam dos servidores HTTP do frontend ou do Uvicorn; usam `TestClient` e um PostgreSQL de teste.

Para uma visão das pastas, arquivos e do fluxo de autenticação, consulte o [mapa visual do projeto](../docs/estrutura-projeto.md).

## Encerrar

Pressione `Ctrl+C` em cada terminal para encerrar o servidor Vite e o Uvicorn.
