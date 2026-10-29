from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client, codigo: str = "PRD-US07"):
    return client.post(
        "/api/produtos",
        json={"codigo": codigo, "nome": "Produto US07", "unidade": "un"},
    )


def _cadastrar_ordem(client, dados):
    return client.post(
        "/api/ordens-producao",
        json=dados,
        headers={"Idempotency-Key": str(uuid4())},
    )


def test_planejador_cadastra_ordem_com_dados_validos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()

    response = _cadastrar_ordem(
        client,
        {"codigo": " op-001 ", "produto_id": produto["id_produto"], "quantidade": "12.500"},
    )

    assert response.status_code == 201
    ordem = response.json()
    assert ordem["codigo"] == "OP-001"
    assert ordem["produto_id"] == produto["id_produto"]
    assert Decimal(str(ordem["quantidade"])) == Decimal("12.500")
    assert ordem["status"] == "PENDENTE"
    assert ordem["id_ordem"]
    assert ordem["criado_em"]

    with state.engine.connect() as connection:
        salvo = connection.execute(
            text("SELECT codigo, produto_id, quantidade, status, criado_por FROM ordens_producao WHERE codigo = 'OP-001'")
        ).mappings().one()
    assert salvo["codigo"] == "OP-001"
    assert str(salvo["produto_id"]) == produto["id_produto"]
    assert Decimal(str(salvo["quantidade"])) == Decimal("12.500")
    assert salvo["status"] == "PENDENTE"
    assert str(salvo["criado_por"]) == str(state.user_id)


def test_cadastro_sem_campo_obrigatorio_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()

    response = _cadastrar_ordem(
        client,
        {"codigo": "OP-002", "produto_id": produto["id_produto"]},
    )

    assert response.status_code == 422
    assert any(erro["loc"][-1] == "quantidade" for erro in response.json()["detail"])


def test_codigo_em_branco_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()

    response = _cadastrar_ordem(
        client,
        {"codigo": "   ", "produto_id": produto["id_produto"], "quantidade": 2},
    )

    assert response.status_code == 422
    assert any(erro["loc"][-1] == "codigo" for erro in response.json()["detail"])


def test_quantidade_deve_ser_positiva(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()

    response = _cadastrar_ordem(
        client,
        {"codigo": "OP-003", "produto_id": produto["id_produto"], "quantidade": 0},
    )

    assert response.status_code == 422


def test_nao_cadastra_ordem_com_produto_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_ordem(
        client,
        {"codigo": "OP-004", "produto_id": str(uuid4()), "quantidade": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado."


def test_codigo_da_ordem_nao_pode_ser_duplicado(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()
    dados = {"codigo": "OP-005", "produto_id": produto["id_produto"], "quantidade": 1}

    primeira = _cadastrar_ordem(client, dados)
    duplicada = _cadastrar_ordem(client, {**dados, "codigo": "op-005"})

    assert primeira.status_code == 201
    assert duplicada.status_code == 409
    assert duplicada.json()["detail"] == "Já existe uma ordem de produção com este código."


def test_operador_nao_pode_cadastrar_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()
    assert client.post("/api/auth/logout").status_code == 204
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = _cadastrar_ordem(
        client,
        {"codigo": "OP-006", "produto_id": produto["id_produto"], "quantidade": 1},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso não autorizado para este perfil."
    with state.engine.connect() as connection:
        total = connection.scalar(text("SELECT count(*) FROM ordens_producao WHERE codigo = 'OP-006'"))
    assert total == 0


def test_planejador_lista_ordens_cadastradas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client).json()
    criado = _cadastrar_ordem(
        client,
        {"codigo": "OP-007", "produto_id": produto["id_produto"], "quantidade": 4},
    )
    assert criado.status_code == 201

    response = client.get("/api/ordens-producao")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["codigo"] == "OP-007"


def test_cadastro_exige_autenticacao(seeded_auth):
    client = seeded_auth.client
    response = _cadastrar_ordem(
        client,
        {"codigo": "OP-008", "produto_id": str(uuid4()), "quantidade": 1},
    )
    assert response.status_code == 401
