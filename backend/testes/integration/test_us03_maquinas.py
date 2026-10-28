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


def test_cadastro_normaliza_codigo_e_nome_e_aceita_descricao_opcional(
    seeded_auth,
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(
        client,
        {
            "codigo": "  maq-006  ",
            "nome": "  Torno  ",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["codigo"] == "MAQ-006"
    assert body["nome"] == "Torno"
    assert body["descricao"] is None

    with state.engine.connect() as connection:
        maquina = connection.execute(
            text(
                """
                SELECT codigo, nome, descricao
                FROM maquinas
                WHERE codigo = 'MAQ-006'
                """
            )
        ).mappings().one()

    assert maquina["codigo"] == "MAQ-006"
    assert maquina["nome"] == "Torno"
    assert maquina["descricao"] is None


def test_cadastro_de_maquina_sem_campo_obrigatorio_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(client, {"codigo": "MAQ-002"})

    assert response.status_code == 422
    erros = response.json()["detail"]
    assert any(erro["loc"][-1] == "nome" for erro in erros)

    response = _cadastrar_maquina(client, {"nome": "Cortadora"})

    assert response.status_code == 422
    erros = response.json()["detail"]
    assert any(erro["loc"][-1] == "codigo" for erro in erros)


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


def test_cadastro_de_maquina_com_codigo_em_branco_nao_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _cadastrar_maquina(
        client,
        {"codigo": "   ", "nome": "Cortadora"},
    )

    assert response.status_code == 422
    assert any(
        erro["loc"][-1] == "codigo"
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


def test_usuario_sem_autenticacao_nao_pode_cadastrar_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    response = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-007", "nome": "Máquina sem autenticação"},
    )

    assert response.status_code == 401
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM maquinas WHERE codigo = 'MAQ-007'")
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


def test_planejador_edita_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    criada = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-020", "nome": "Cortadora"},
    )
    id_maquina = criada.json()["id_maquina"]

    response = client.put(
        f"/api/maquinas/{id_maquina}",
        json={
            "codigo": " maq-021 ",
            "nome": "  Cortadora CNC  ",
            "descricao": "  Corte automatizado  ",
        },
    )

    assert response.status_code == 200
    assert response.json()["codigo"] == "MAQ-021"
    assert response.json()["nome"] == "Cortadora CNC"
    assert response.json()["descricao"] == "Corte automatizado"
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM maquinas WHERE codigo = 'MAQ-021'")
        )
    assert total == 1


def test_planejador_altera_status_sem_excluir_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    criada = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-022", "nome": "Prensa"},
    )
    id_maquina = criada.json()["id_maquina"]

    inativada = client.patch(
        f"/api/maquinas/{id_maquina}/status",
        json={"ativo": False},
    )
    assert inativada.status_code == 200
    assert inativada.json()["ativo"] is False

    reativada = client.patch(
        f"/api/maquinas/{id_maquina}/status",
        json={"ativo": True},
    )
    assert reativada.status_code == 200
    assert reativada.json()["ativo"] is True

    with state.engine.connect() as connection:
        maquina = connection.execute(
            text("SELECT ativo FROM maquinas WHERE codigo = 'MAQ-022'")
        ).scalar_one()
    assert maquina is True


def test_planejador_exclui_maquina_sem_vinculos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    criada = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-023", "nome": "Furadeira"},
    )

    response = client.delete(
        f"/api/maquinas/{criada.json()['id_maquina']}"
    )

    assert response.status_code == 204
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM maquinas WHERE codigo = 'MAQ-023'")
        )
    assert total == 0


def test_exclusao_de_maquina_vinculada_e_bloqueada(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    criada = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-024", "nome": "Fresadora"},
    )
    id_maquina = criada.json()["id_maquina"]
    table_name = "vinculo_maquina_us03_teste"

    with state.engine.begin() as connection:
        connection.execute(
            text(
                f"""
                CREATE TABLE {table_name} (
                    id_maquina UUID NOT NULL
                    REFERENCES maquinas(id_maquina) ON DELETE RESTRICT
                )
                """
            )
        )
        connection.execute(
            text(f"INSERT INTO {table_name} (id_maquina) VALUES (:id)"),
            {"id": id_maquina},
        )

    try:
        response = client.delete(f"/api/maquinas/{id_maquina}")

        assert response.status_code == 409
        assert "registros vinculados" in response.json()["detail"]
        with state.engine.connect() as connection:
            total = connection.scalar(
                text("SELECT count(*) FROM maquinas WHERE codigo = 'MAQ-024'")
            )
        assert total == 1
    finally:
        with state.engine.begin() as connection:
            connection.execute(text(f"DROP TABLE {table_name}"))


def test_operador_nao_pode_alterar_maquina(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    criada = _cadastrar_maquina(
        client,
        {"codigo": "MAQ-025", "nome": "Torno"},
    )
    id_maquina = criada.json()["id_maquina"]
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = client.patch(
        f"/api/maquinas/{id_maquina}/status",
        json={"ativo": False},
    )

    assert response.status_code == 403
    response = client.put(
        f"/api/maquinas/{id_maquina}",
        json={"codigo": "MAQ-026", "nome": "Máquina alterada"},
    )
    assert response.status_code == 403

    response = client.delete(f"/api/maquinas/{id_maquina}")
    assert response.status_code == 403

    with state.engine.connect() as connection:
        maquina = connection.execute(
            text(
                "SELECT codigo, nome, ativo FROM maquinas "
                "WHERE codigo = 'MAQ-025'"
            )
        ).mappings().one()
    assert maquina["codigo"] == "MAQ-025"
    assert maquina["nome"] == "Torno"
    assert maquina["ativo"] is True
