"""Testes de integração do cadastro de famílias de produtos (US05)."""


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def test_cadastro_valido_cria_familia_para_planejador(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = client.post(
        "/api/families",
        json={
            "code": " fam-001 ",
            "name": "  Família de embalagens  ",
            "description": "  Produtos usados em embalagens.  ",
        },
    )

    assert response.status_code == 201
    familia = response.json()
    assert familia["code"] == "FAM-001"
    assert familia["name"] == "Família de embalagens"
    assert familia["description"] == "Produtos usados em embalagens."
    assert familia["is_active"] is True
    assert familia["version"] == 1
    assert familia["id"]


def test_cadastro_rejeita_campos_obrigatorios_ausentes(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = client.post("/api/families", json={"code": "FAM-002"})

    assert response.status_code == 422
    assert any(item["loc"][-1] == "name" for item in response.json()["detail"])
    assert client.get("/api/families").json() == []


def test_cadastro_rejeita_nome_em_branco(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = client.post(
        "/api/families",
        json={"code": "FAM-003", "name": "   "},
    )

    assert response.status_code == 422
    assert any(item["loc"][-1] == "name" for item in response.json()["detail"])


def test_codigo_duplicado_retorna_conflito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    payload = {"code": "FAM-004", "name": "Família A"}

    primeira = client.post("/api/families", json=payload)
    segunda = client.post(
        "/api/families",
        json={"code": "fam-004", "name": "Família B"},
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == (
        "Já existe uma família cadastrada com este código."
    )


def test_operador_nao_pode_cadastrar_familia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = client.post(
        "/api/families",
        json={"code": "FAM-005", "name": "Família restrita"},
    )

    assert response.status_code == 403


def test_cadastro_exige_usuario_autenticado(seeded_auth):
    response = seeded_auth.client.post(
        "/api/families",
        json={"code": "FAM-006", "name": "Família sem sessão"},
    )

    assert response.status_code == 401


def test_listagem_retorna_familias_cadastradas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    client.post(
        "/api/families",
        json={"code": "FAM-007", "name": "Família Z"},
    )
    client.post(
        "/api/families",
        json={"code": "FAM-008", "name": "Família A"},
    )

    response = client.get("/api/families")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Família A", "Família Z"]
