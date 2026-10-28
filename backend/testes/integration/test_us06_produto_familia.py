from uuid import uuid4

from sqlalchemy import text


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client, codigo: str = "PRD-001"):
    return client.post(
        "/api/produtos",
        json={
            "codigo": codigo,
            "nome": "Produto Teste",
            "unidade": "un",
        },
    )


def _criar_familia(client, codigo: str = "FAM-001"):
    return client.post(
        "/api/families",
        json={
            "code": codigo,
            "name": f"Família {codigo}",
        },
    )


def _associar_familia(client, produto_id: str, family_id):
    return client.patch(
        f"/api/produtos/{produto_id}/familia",
        json={"family_id": family_id},
    )


def test_planejador_associa_produto_a_familia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client).json()
    familia = _criar_familia(client).json()

    response = _associar_familia(
        client,
        produto["id_produto"],
        familia["id"],
    )

    assert response.status_code == 200
    assert response.json()["family_id"] == familia["id"]

    with state.engine.connect() as connection:
        family_id = connection.scalar(
            text(
                """
                SELECT family_id
                FROM produtos
                WHERE id_produto = :produto_id
                """
            ),
            {"produto_id": produto["id_produto"]},
        )

    assert str(family_id) == familia["id"]


def test_planejador_pode_trocar_familia_do_produto(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client).json()
    familia_a = _criar_familia(client, "FAM-001").json()
    familia_b = _criar_familia(client, "FAM-002").json()

    primeira = _associar_familia(
        client,
        produto["id_produto"],
        familia_a["id"],
    )

    segunda = _associar_familia(
        client,
        produto["id_produto"],
        familia_b["id"],
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert segunda.json()["family_id"] == familia_b["id"]


def test_planejador_remove_associacao_de_familia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client).json()
    familia = _criar_familia(client).json()

    associacao = _associar_familia(
        client,
        produto["id_produto"],
        familia["id"],
    )

    assert associacao.status_code == 200

    response = _associar_familia(
        client,
        produto["id_produto"],
        None,
    )

    assert response.status_code == 200
    assert response.json()["family_id"] is None


def test_associacao_rejeita_produto_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    familia = _criar_familia(client).json()

    response = _associar_familia(
        client,
        str(uuid4()),
        familia["id"],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado."


def test_associacao_rejeita_familia_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client).json()

    response = _associar_familia(
        client,
        produto["id_produto"],
        str(uuid4()),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Família não encontrada."


def test_operador_nao_pode_associar_produto_a_familia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client).json()
    familia = _criar_familia(client).json()

    client.post("/api/auth/logout")

    assert _login(
        client,
        state.operator_email,
        state.password,
    ).status_code == 200

    response = _associar_familia(
        client,
        produto["id_produto"],
        familia["id"],
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Acesso não autorizado para este perfil."
    )


def test_associacao_exige_usuario_autenticado(seeded_auth):
    client = seeded_auth.client

    response = _associar_familia(
        client,
        str(uuid4()),
        None,
    )

    assert response.status_code == 401
