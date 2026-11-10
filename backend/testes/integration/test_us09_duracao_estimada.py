from uuid import uuid4

import pytest
from sqlalchemy import text


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client):
    response = client.post(
        "/api/produtos",
        json={"codigo": "PRD-US09", "nome": "Produto US09", "unidade": "un"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _criar_ordem(client, produto_id: str, codigo: str = "OP-US09"):
    response = client.post(
        "/api/ordens-producao",
        json={"codigo": codigo, "produto_id": produto_id, "quantidade": 5},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _atualizar_duracao(client, ordem_id: str, duracao):
    return client.patch(
        f"/api/ordens-producao/{ordem_id}/duracao-estimada",
        json={"duracao_estimada_minutos": duracao},
    )


def test_planejador_salva_duracao_estimada_valida(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    ordem = _criar_ordem(client, produto["id_produto"])

    response = _atualizar_duracao(client, ordem["id_ordem"], 120)

    assert response.status_code == 200, response.text
    assert response.json()["duracao_estimada_minutos"] == 120

    lista = client.get("/api/ordens-producao")
    assert lista.status_code == 200
    ordem_listada = next(item for item in lista.json() if item["id_ordem"] == ordem["id_ordem"])
    assert ordem_listada["duracao_estimada_minutos"] == 120

    with state.engine.connect() as connection:
        salvo = connection.execute(
            text("SELECT duracao_estimada_minutos FROM ordens_producao WHERE codigo = :codigo"),
            {"codigo": ordem["codigo"]},
        ).scalar_one()
    assert salvo == 120


@pytest.mark.parametrize("duracao_invalida", [0, -1, 1.5, "inválida", None, True])
def test_duracao_estimada_invalida_nao_e_salva(seeded_auth, duracao_invalida):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    ordem = _criar_ordem(client, produto["id_produto"])

    response = _atualizar_duracao(client, ordem["id_ordem"], duracao_invalida)

    assert response.status_code == 422
    assert "duração estimada é inválida" in str(response.json()).lower()

    with state.engine.connect() as connection:
        salvo = connection.execute(
            text("SELECT duracao_estimada_minutos FROM ordens_producao WHERE codigo = :codigo"),
            {"codigo": ordem["codigo"]},
        ).scalar_one()
    assert salvo is None


def test_duracao_estimada_de_ordem_inexistente_retorna_404(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    response = _atualizar_duracao(client, str(uuid4()), 60)

    assert response.status_code == 404
    assert response.json()["detail"] == "Ordem de produção não encontrada."


def test_atualizar_duracao_exige_autenticacao(seeded_auth):
    response = _atualizar_duracao(seeded_auth.client, str(uuid4()), 60)

    assert response.status_code == 401


def test_operador_nao_pode_atualizar_duracao_estimada(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    ordem = _criar_ordem(client, produto["id_produto"])
    assert client.post("/api/auth/logout").status_code == 204
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = _atualizar_duracao(client, ordem["id_ordem"], 60)

    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso não autorizado para este perfil."
    with state.engine.connect() as connection:
        salvo = connection.execute(
            text("SELECT duracao_estimada_minutos FROM ordens_producao WHERE codigo = :codigo"),
            {"codigo": ordem["codigo"]},
        ).scalar_one()
    assert salvo is None
