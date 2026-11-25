from uuid import uuid4

import pytest
from sqlalchemy import text


SUGESTOES = "/api/planejamentos/sugestoes"


def _post(client, rota, dados, **kwargs):
    resposta = client.post(rota, json=dados, **kwargs)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _maquina(client, codigo):
    return _post(client, "/api/maquinas", {
        "codigo": codigo,
        "nome": f"Máquina {codigo}",
    })["id_maquina"]


def _familia(client, codigo):
    return _post(client, "/api/families", {
        "code": codigo,
        "name": f"Família {codigo}",
    })["id"]


def _ordem(client, codigo, familia, maquinas):
    produto = _post(client, "/api/produtos", {
        "codigo": f"PROD-{codigo}",
        "nome": f"Produto {codigo}",
        "unidade": "un",
    })

    produto_id = produto["id_produto"]

    resposta = client.patch(
        f"/api/produtos/{produto_id}/familia",
        json={"family_id": familia},
    )
    assert resposta.status_code == 200, resposta.text

    resposta = client.put(
        f"/api/produtos/{produto_id}/maquinas",
        json={"maquinas_ids": maquinas},
    )
    assert resposta.status_code == 200, resposta.text

    return _post(client, "/api/ordens-producao", {
        "codigo": codigo,
        "produto_id": produto_id,
        "quantidade": 10,
    }, headers={"Idempotency-Key": str(uuid4())})


def _confirmar_persistencia(engine, sugestoes, itens):
    with engine.connect() as conexao:
        assert conexao.scalar(text(
            "SELECT count(*) FROM sugestoes_planejamento"
        )) == sugestoes

        assert conexao.scalar(text(
            "SELECT count(*) FROM itens_sugestao_planejamento"
        )) == itens


@pytest.fixture
def cenario(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    resposta = client.post("/api/auth/login", json={
        "email": state.email,
        "password": state.password,
    })

    assert resposta.status_code == 200, resposta.text

    return client, state


def test_associa_maquinas_compativeis_e_persiste_sugestao(cenario):
    client, state = cenario

    a = _familia(client, "A")
    b = _familia(client, "B")

    m1 = _maquina(client, "M01")
    m2 = _maquina(client, "M02")

    op1 = _ordem(client, "OP01", a, [m1])["id_ordem"]
    op2 = _ordem(client, "OP02", b, [m2])["id_ordem"]

    sugestao = _post(client, SUGESTOES, {
        "ordens_ids": [op1, op2],
    })

    assert sugestao["tempo_setup_original_minutos"] == 0
    assert sugestao["tempo_setup_total_minutos"] == 0

    assert {
        item["ordem_id"]: item["maquina_id"]
        for item in sugestao["itens"]
    } == {op1: m1, op2: m2}

    assert all(
        item["setup_minutos"] == 0
        for item in sugestao["itens"]
    )

    consulta = client.get(
        f"{SUGESTOES}/{sugestao['id_sugestao']}"
    )

    assert consulta.status_code == 200
    assert consulta.json() == sugestao

    _confirmar_persistencia(state.engine, 1, 2)


def test_distribui_ordens_e_desconsidera_maquina_inativa(cenario):
    client, state = cenario

    familia = _familia(client, "A")

    m1 = _maquina(client, "M01")
    m2 = _maquina(client, "M02")
    m3 = _maquina(client, "M03")

    ordens = [
        _ordem(client, f"OP0{i}", familia, [m1, m2, m3])
        ["id_ordem"]
        for i in range(1, 4)
    ]

    resposta = client.patch(
        f"/api/maquinas/{m1}/status",
        json={"ativo": False},
    )
    assert resposta.status_code == 200

    sugestao = _post(client, SUGESTOES, {
        "ordens_ids": ordens,
    })

    assert {
        item["ordem_id"]: item["maquina_id"]
        for item in sugestao["itens"]
    } == {
        ordens[0]: m2,
        ordens[1]: m3,
        ordens[2]: m2,
    }

    _confirmar_persistencia(state.engine, 1, 3)


@pytest.mark.parametrize("somente_inativa", [False, True])
def test_bloqueia_ordem_sem_maquina_compativel_ativa(
    cenario, somente_inativa
):
    client, state = cenario

    familia = _familia(client, "A")
    m1 = _maquina(client, "M01")
    m2 = _maquina(client, "M02")

    op1 = _ordem(client, "OP01", familia, [m2])
    op2 = _ordem(
        client, "OP02", familia,
        [m1] if somente_inativa else [],
    )

    if somente_inativa:
        resposta = client.patch(
            f"/api/maquinas/{m1}/status",
            json={"ativo": False},
        )
        assert resposta.status_code == 200

    resposta = client.post(SUGESTOES, json={
        "ordens_ids": [op1["id_ordem"], op2["id_ordem"]],
    })

    assert resposta.status_code == 422

    detalhe = resposta.json()["detail"]

    assert "OP02" in detalhe
    assert "PROD-OP02" in detalhe
    assert "não possui máquina compatível ativa" in detalhe

    _confirmar_persistencia(state.engine, 0, 0)


def test_exige_setup_entre_familias_da_mesma_maquina(cenario):
    client, state = cenario

    a = _familia(client, "A")
    b = _familia(client, "B")

    maquina = _maquina(client, "M01")

    op1 = _ordem(client, "OP01", a, [maquina])["id_ordem"]
    op2 = _ordem(client, "OP02", b, [maquina])["id_ordem"]

    resposta = client.post(SUGESTOES, json={
        "ordens_ids": [op1, op2],
    })

    assert resposta.status_code == 422
    assert "A → B sem cadastro" in resposta.json()["detail"]
    assert "B → A sem cadastro" in resposta.json()["detail"]

    _confirmar_persistencia(state.engine, 0, 0)


def test_preserva_maquina_da_sugestao_apos_alterar_compatibilidade(
    cenario
):
    client, state = cenario

    familia = _familia(client, "A")
    m1 = _maquina(client, "M01")
    m2 = _maquina(client, "M02")

    ordem = _ordem(client, "OP01", familia, [m1])

    sugestao = _post(client, SUGESTOES, {
        "ordens_ids": [ordem["id_ordem"]],
    })

    resposta = client.put(
        f"/api/produtos/{ordem['produto_id']}/maquinas",
        json={"maquinas_ids": [m2]},
    )
    assert resposta.status_code == 200

    consulta = client.get(
        f"{SUGESTOES}/{sugestao['id_sugestao']}"
    )

    assert consulta.status_code == 200
    assert consulta.json()["itens"][0]["maquina_id"] == m1

    nova_sugestao = _post(client, SUGESTOES, {
        "ordens_ids": [ordem["id_ordem"]],
    })

    assert nova_sugestao["itens"][0]["maquina_id"] == m2

    _confirmar_persistencia(state.engine, 2, 2)
