from sqlalchemy import text


def _login(client, email, password):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _cadastrar_maquina(client, dados):
    return client.post("/api/maquinas", json=dados)


def test_planejador_cadastra_maquina_com_dados_validos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(
        client,
        {
            "codigo": "maq-001",
            "nome": "Cortadora",
            "descricao": "Corte de chapas",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["codigo"] == "MAQ-001"
    assert body["nome"] == "Cortadora"
    assert body["descricao"] == "Corte de chapas"
    assert body["ativo"] is True
    assert body["id_maquina"]
    assert body["criado_em"]

    with state.engine.connect() as connection:
        maquina = connection.execute(
            text(
                """
                SELECT codigo, nome, descricao, ativo
                FROM maquinas
                WHERE codigo = 'MAQ-001'
                """
            )
        ).mappings().one()

    assert maquina["codigo"] == "MAQ-001"
    assert maquina["nome"] == "Cortadora"
    assert maquina["descricao"] == "Corte de chapas"
    assert maquina["ativo"] is True


def test_cadastro_de_maquina_sem_campo_obrigatorio_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(client, {"codigo": "MAQ-002"})

    assert response.status_code == 422
    erros = response.json()["detail"]
    assert any(erro["loc"][-1] == "nome" for erro in erros)


def test_cadastro_de_maquina_com_nome_em_branco_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-003", "nome": "   "},
    )

    assert response.status_code == 422
    assert any(
        erro["loc"][-1] == "nome"
        for erro in response.json()["detail"]
    )


def test_codigo_de_maquina_nao_pode_ser_duplicado(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    first = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-004", "nome": "Cortadora"},
    )
    duplicate = _cadastrar_maquina(
        client,
        {"codigo": "maq-004", "nome": "Outra cortadora"},
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "Já existe uma máquina com este código."
    )


def test_operador_nao_pode_cadastrar_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert (
        _login(client, state.operator_email, state.password).status_code
        == 200
    )

    response = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-005", "nome": "Máquina bloqueada"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Acesso não autorizado para este perfil."
    )
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM maquinas WHERE codigo = 'MAQ-005'")
        )
    assert total == 0


def test_planejador_lista_maquinas_cadastradas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    first = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-010", "nome": "Cortadora"},
    )
    second = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-011", "nome": "Prensa"},
    )
    response = client.get("/api/maquinas")

    assert first.status_code == 201
    assert second.status_code == 201
    assert response.status_code == 200
    maquinas = response.json()
    assert [maquina["codigo"] for maquina in maquinas] == [
        "MAQ-010",
        "MAQ-011",
    ]


def test_operador_nao_pode_listar_maquinas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert (
        _login(client, state.operator_email, state.password).status_code
        == 200
    )

    response = client.get("/api/maquinas")

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Acesso não autorizado para este perfil."
    )
