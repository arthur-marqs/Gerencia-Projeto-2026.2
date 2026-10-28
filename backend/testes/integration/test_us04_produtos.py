from sqlalchemy import text


def _login(client, email, password):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _cadastrar_produto(client, dados):
    return client.post(
        "/api/produtos",
        json=dados,
    )


def test_planejador_cadastra_produto_com_dados_validos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    response = _cadastrar_produto(
        client,
        {
            "codigo": "prd-001",
            "nome": "Produto Teste",
            "unidade": "un",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["codigo"] == "PRD-001"
    assert body["nome"] == "Produto Teste"
    assert body["unidade"] == "un"
    assert body["ativo"] is True
    assert body["id_produto"]
    assert body["criado_em"]

    with state.engine.connect() as connection:
        produto = connection.execute(
            text(
                """
                SELECT codigo, nome, unidade, ativo
                FROM produtos
                WHERE codigo = 'PRD-001'
                """
            )
        ).mappings().one()

    assert produto["codigo"] == "PRD-001"
    assert produto["nome"] == "Produto Teste"
    assert produto["unidade"] == "un"
    assert produto["ativo"] is True


def test_cadastro_sem_campo_obrigatorio_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    response = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-002",
            "nome": "Produto Teste",
        },
    )

    assert response.status_code == 422

    erros = response.json()["detail"]

    assert any(
        erro["loc"][-1] == "unidade"
        for erro in erros
    )


def test_cadastro_com_campo_apenas_espacos_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    response = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-003",
            "nome": "   ",
            "unidade": "un",
        },
    )

    assert response.status_code == 422

    erros = response.json()["detail"]

    assert any(
        erro["loc"][-1] == "nome"
        for erro in erros
    )


def test_codigo_de_produto_nao_pode_ser_duplicado(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    primeiro = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-004",
            "nome": "Produto Um",
            "unidade": "un",
        },
    )

    assert primeiro.status_code == 201

    duplicado = _cadastrar_produto(
        client,
        {
            "codigo": "prd-004",
            "nome": "Produto Dois",
            "unidade": "un",
        },
    )

    assert duplicado.status_code == 409
    assert duplicado.json()["detail"] == (
        "Já existe um produto com este código."
    )


def test_operador_nao_pode_cadastrar_produto(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(
        client,
        state.operator_email,
        state.password,
    )

    assert login.status_code == 200

    response = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-005",
            "nome": "Produto Bloqueado",
            "unidade": "un",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Acesso não autorizado para este perfil."
    )

    with state.engine.connect() as connection:
        total = connection.scalar(
            text(
                """
                SELECT count(*)
                FROM produtos
                WHERE codigo = 'PRD-005'
                """
            )
        )

    assert total == 0


def test_planejador_lista_produtos_cadastrados(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    primeiro = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-010",
            "nome": "Produto Dez",
            "unidade": "un",
        },
    )

    segundo = _cadastrar_produto(
        client,
        {
            "codigo": "PRD-011",
            "nome": "Produto Onze",
            "unidade": "kg",
        },
    )

    assert primeiro.status_code == 201
    assert segundo.status_code == 201

    response = client.get("/api/produtos")

    assert response.status_code == 200

    produtos = response.json()

    assert len(produtos) == 2
    assert produtos[0]["codigo"] == "PRD-010"
    assert produtos[0]["nome"] == "Produto Dez"
    assert produtos[1]["codigo"] == "PRD-011"
    assert produtos[1]["nome"] == "Produto Onze"


def test_operador_nao_pode_listar_produtos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = _login(
        client,
        state.operator_email,
        state.password,
    )

    assert login.status_code == 200

    response = client.get("/api/produtos")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Acesso não autorizado para este perfil."
    )
