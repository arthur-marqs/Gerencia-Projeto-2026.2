from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy import text


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_ordem(client, codigo: str):
    produto = client.post(
        "/api/produtos",
        json={"codigo": f"PRD-{codigo}", "nome": "Produto US08", "unidade": "un"},
    ).json()
    return client.post(
        "/api/ordens-producao",
        json={
            "codigo": codigo,
            "produto_id": produto["id_produto"],
            "quantidade": 2,
        },
    ).json()


def _dados_validos(**sobrescritos):
    return {
        "prazo": (date.today() + timedelta(days=7)).isoformat(),
        "prioridade": "Média",
        **sobrescritos,
    }


def test_planejador_define_altera_e_consulta_prazo_prioridade(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-001")

    primeira_atualizacao = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json=_dados_validos(),
    )

    assert primeira_atualizacao.status_code == 200
    primeira = primeira_atualizacao.json()
    assert primeira["id_ordem"] == ordem["id_ordem"]
    assert primeira["prazo"] == _dados_validos()["prazo"]
    assert primeira["prioridade"] == "Média"

    novo_prazo = (date.today() + timedelta(days=14)).isoformat()
    segunda_atualizacao = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json=_dados_validos(prazo=novo_prazo, prioridade="Alta"),
    )

    assert segunda_atualizacao.status_code == 200
    consultada = client.get(f"/api/ordens-producao/{ordem['id_ordem']}")
    assert consultada.status_code == 200
    assert consultada.json()["id_ordem"] == ordem["id_ordem"]
    assert consultada.json()["prazo"] == novo_prazo
    assert consultada.json()["prioridade"] == "Alta"


def test_prazo_ausente_nao_atualiza_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-002")

    response = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json={"prazo": "", "prioridade": "Baixa"},
    )

    assert response.status_code == 422
    assert any(erro["loc"][-1] == "prazo" for erro in response.json()["detail"])
    assert "O prazo é obrigatório." in response.text
    ordem_inalterada = client.get(
        f"/api/ordens-producao/{ordem['id_ordem']}"
    ).json()
    assert ordem_inalterada["prazo"] is None
    assert ordem_inalterada["prioridade"] is None


def test_prazo_no_passado_nao_atualiza_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-003")

    response = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json=_dados_validos(prazo=(date.today() - timedelta(days=1)).isoformat()),
    )

    assert response.status_code == 422
    assert "O prazo não pode estar no passado." in response.text
    ordem_inalterada = client.get(
        f"/api/ordens-producao/{ordem['id_ordem']}"
    ).json()
    assert ordem_inalterada["prazo"] is None
    assert ordem_inalterada["prioridade"] is None


def test_prioridade_ausente_ou_invalida_nao_atualiza_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-004")
    endpoint = f"/api/ordens-producao/{ordem['id_ordem']}"

    ausente = client.put(endpoint, json={"prazo": _dados_validos()["prazo"]})
    invalida = client.put(endpoint, json=_dados_validos(prioridade="Urgente"))

    assert ausente.status_code == 422
    assert any(erro["loc"][-1] == "prioridade" for erro in ausente.json()["detail"])
    assert invalida.status_code == 422
    assert "Uma prioridade válida" in invalida.text
    ordem_inalterada = client.get(endpoint).json()
    assert ordem_inalterada["prazo"] is None
    assert ordem_inalterada["prioridade"] is None


def test_ordem_inexistente_nao_e_criada_ao_tentar_atualizar(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    id_inexistente = uuid4()

    response = client.put(
        f"/api/ordens-producao/{id_inexistente}",
        json=_dados_validos(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ordem de produção não encontrada."
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE id_ordem = :id"),
            {"id": id_inexistente},
        )
    assert total == 0


def test_operador_nao_pode_alterar_prazo_ou_prioridade(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-006")
    assert client.post("/api/auth/logout").status_code == 204
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json=_dados_validos(prioridade="Alta"),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso não autorizado para este perfil."
    with state.engine.connect() as connection:
        salvo = connection.execute(
            text(
                "SELECT prazo, prioridade FROM ordens_producao WHERE id_ordem = :id"
            ),
            {"id": ordem["id_ordem"]},
        ).mappings().one()
    assert salvo["prazo"] is None
    assert salvo["prioridade"] is None


def test_prazo_igual_a_data_atual_e_aceito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, "OP-US08-007")

    response = client.put(
        f"/api/ordens-producao/{ordem['id_ordem']}",
        json=_dados_validos(prazo=date.today().isoformat(), prioridade="Baixa"),
    )

    assert response.status_code == 200
    assert response.json()["prazo"] == date.today().isoformat()
    assert response.json()["prioridade"] == "Baixa"
