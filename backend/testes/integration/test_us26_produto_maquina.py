
from uuid import uuid4

from sqlalchemy import text


def _login(client, email, password):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client):
    response = client.post(
        "/api/produtos",
        json={
            "codigo": "PRD-026",
            "nome": "Produto Teste US26",
            "unidade": "un",
        },
    )
    assert response.status_code == 201
    return response.json()


def _criar_maquina(client, codigo):
    response = client.post(
        "/api/maquinas",
        json={
            "codigo": codigo,
            "nome": f"Maquina {codigo}",
        },
    )
    assert response.status_code == 201
    return response.json()


def _definir_compatibilidade(client, produto_id, maquinas_ids):
    return client.put(
        f"/api/produtos/{produto_id}/maquinas",
        json={"maquinas_ids": maquinas_ids},
    )


def _consultar_compatibilidade(client, produto_id):
    return client.get(
        f"/api/produtos/{produto_id}/maquinas"
    )


def test_planejador_associa_uma_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-026")

    response = _definir_compatibilidade(
        client,
        produto["id_produto"],
        [maquina["id_maquina"]],
    )

    assert response.status_code == 200
    assert response.json()["possui_maquina_compativel"] is True
    assert len(response.json()["maquinas_compativeis"]) == 1

    with state.engine.connect() as connection:
        total = connection.scalar(
            text(
                "SELECT COUNT(*) FROM produto_maquina "
                "WHERE id_produto = :id_produto"
            ),
            {"id_produto": produto["id_produto"]},
        )

    assert total == 1


def test_planejador_associa_varias_maquinas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina_a = _criar_maquina(client, "MAQ-001")
    maquina_b = _criar_maquina(client, "MAQ-002")

    response = _definir_compatibilidade(
        client,
        produto["id_produto"],
        [maquina_a["id_maquina"], maquina_b["id_maquina"]],
    )

    assert response.status_code == 200
    assert len(response.json()["maquinas_compativeis"]) == 2


def test_planejador_consulta_compatibilidades(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-003")

    assert _definir_compatibilidade(
        client, produto["id_produto"], [maquina["id_maquina"]]
    ).status_code == 200

    response = _consultar_compatibilidade(
        client, produto["id_produto"]
    )

    assert response.status_code == 200
    assert response.json()["id_produto"] == produto["id_produto"]
    assert response.json()["maquinas_compativeis"][0]["codigo"] == "MAQ-003"


def test_produto_sem_maquina_compativel(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    response = _consultar_compatibilidade(
        client, produto["id_produto"]
    )

    assert response.status_code == 200
    assert response.json()["maquinas_compativeis"] == []
    assert response.json()["possui_maquina_compativel"] is False


def test_planejador_substitui_compatibilidades(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina_a = _criar_maquina(client, "MAQ-004")
    maquina_b = _criar_maquina(client, "MAQ-005")

    assert _definir_compatibilidade(
        client, produto["id_produto"], [maquina_a["id_maquina"]]
    ).status_code == 200

    response = _definir_compatibilidade(
        client, produto["id_produto"], [maquina_b["id_maquina"]]
    )

    assert response.status_code == 200
    assert len(response.json()["maquinas_compativeis"]) == 1
    assert response.json()["maquinas_compativeis"][0]["id_maquina"] == (
        maquina_b["id_maquina"]
    )


def test_planejador_remove_todas_compatibilidades(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-006")

    assert _definir_compatibilidade(
        client, produto["id_produto"], [maquina["id_maquina"]]
    ).status_code == 200

    response = _definir_compatibilidade(
        client, produto["id_produto"], []
    )

    assert response.status_code == 200
    assert response.json()["maquinas_compativeis"] == []
    assert response.json()["possui_maquina_compativel"] is False


def test_compatibilidade_rejeita_produto_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    response = _definir_compatibilidade(client, str(uuid4()), [])

    assert response.status_code == 404


def test_compatibilidade_rejeita_maquina_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)

    response = _definir_compatibilidade(
        client, produto["id_produto"], [str(uuid4())]
    )

    assert response.status_code == 404


def test_compatibilidade_rejeita_maquina_duplicada(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-007")

    response = _definir_compatibilidade(
        client,
        produto["id_produto"],
        [maquina["id_maquina"], maquina["id_maquina"]],
    )

    assert response.status_code == 422


def test_compatibilidade_rejeita_maquina_inativa(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-008")

    assert client.patch(
        f"/api/maquinas/{maquina['id_maquina']}/status",
        json={"ativo": False},
    ).status_code == 200

    response = _definir_compatibilidade(
        client, produto["id_produto"], [maquina["id_maquina"]]
    )

    assert response.status_code == 422


def test_operador_nao_pode_definir_compatibilidade(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(client, state.email, state.password).status_code == 200

    produto = _criar_produto(client)
    maquina = _criar_maquina(client, "MAQ-009")

    assert client.post("/api/auth/logout").status_code == 204

    assert _login(
        client, state.operator_email, state.password
    ).status_code == 200

    response = _definir_compatibilidade(
        client, produto["id_produto"], [maquina["id_maquina"]]
    )

    assert response.status_code == 403

    consulta = _consultar_compatibilidade(
        client, produto["id_produto"]
    )

    assert consulta.status_code == 403


def test_compatibilidade_exige_autenticacao(seeded_auth):
    client = seeded_auth.client

    response = _consultar_compatibilidade(client, str(uuid4()))

    assert response.status_code == 401
