from uuid import uuid4

from sqlalchemy import text

from testes.integration.test_us13_sequencia_sugerida import (
    SUGESTOES,
    _confirmar_sugestoes_salvas,
    _login,
    _ordem,
    _post,
    _setup,
    cenario_ab,
)

PLANOS = "/api/planejamentos"


def test_compara_a_sugestao_mais_recente_com_as_mesmas_ordens(cenario_ab):
    client, state, a, b, (op01, op02, op03) = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    ordens = [op01, op02, op03]
    plano = _post(client, PLANOS, {"nome": "Manual", "ordens_ids": ordens})
    _post(client, SUGESTOES, {"ordens_ids": [op03, op02, op01]})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})
    op04 = _ordem(client, "OP04", a)["id_ordem"]
    _post(client, SUGESTOES, {"ordens_ids": [*ordens, op04]})
    rota_plano = f"{PLANOS}/{plano['id_planejamento']}"

    resposta = client.get(f"{rota_plano}/comparacao")

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == {
        "planejamento": plano,
        "sugestao": sugestao,
        "setup": {
            "manual_minutos": 50,
            "sugerido_minutos": 20,
            "diferenca_minutos": -30,
            "referencia": "registrado",
        },
    }
    assert [item["ordem_id"] for item in plano["itens"]] == [op01, op02, op03]
    assert [item["ordem_id"] for item in sugestao["itens"]] == [op01, op03, op02]
    assert client.get(rota_plano).json() == plano
    assert client.get(f"{SUGESTOES}/{sugestao['id_sugestao']}").json() == sugestao
    _confirmar_sugestoes_salvas(state.engine, 3, 10)


def test_requer_sugestao_para_o_conjunto_de_ordens_do_planejamento(cenario_ab):
    client, state, _, _, (op01, op02, op03) = cenario_ab
    plano = _post(client, PLANOS, {"nome": "Manual", "ordens_ids": [op01, op02, op03]})
    _post(client, SUGESTOES, {"ordens_ids": [op01, op03]})
    rota_plano = f"{PLANOS}/{plano['id_planejamento']}"

    resposta = client.get(f"{rota_plano}/comparacao")

    assert resposta.status_code == 404, resposta.text
    assert resposta.json() == {
        "detail": "Gere uma sequência sugerida para este planejamento antes de comparar.",
    }
    assert client.get(rota_plano).json() == plano
    _confirmar_sugestoes_salvas(state.engine, 1, 2)

    inexistente = client.get(f"{PLANOS}/{uuid4()}/comparacao")
    assert inexistente.status_code == 404
    assert inexistente.json() == {"detail": "Planejamento não encontrado."}


def test_recalcula_setup_por_maquina_quando_o_manual_muda(cenario_ab):
    client, state, a, b, (op01, op02, op03) = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    maquina = _post(client, "/api/maquinas", {"codigo": "M02", "nome": "Máquina M02"})
    op04 = _ordem(client, "OP04", b)
    compatibilidade = client.put(
        f"/api/produtos/{op04['produto_id']}/maquinas",
        json={"maquinas_ids": [maquina["id_maquina"]]},
    )
    assert compatibilidade.status_code == 200, compatibilidade.text
    ordens = [op01, op04["id_ordem"], op02, op03]
    plano = _post(client, PLANOS, {"nome": "Manual", "ordens_ids": ordens})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})
    rota_plano = f"{PLANOS}/{plano['id_planejamento']}"
    nova_ordem = [op02, op01, op04["id_ordem"], op03]
    alterado = client.put(rota_plano, json={"nome": "Manual", "ordens_ids": nova_ordem})
    assert alterado.status_code == 200, alterado.text

    resposta = client.get(f"{rota_plano}/comparacao")

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["planejamento"] == alterado.json()
    assert resposta.json()["sugestao"] == sugestao
    assert resposta.json()["setup"] == {
        "manual_minutos": 30,
        "sugerido_minutos": 20,
        "diferenca_minutos": -10,
        "referencia": "atual",
    }

    with state.engine.begin() as conexao:
        conexao.execute(
            text("DELETE FROM tempos_setup_familias WHERE familia_origem_id = :origem"),
            {"origem": b},
        )
    sem_setup = client.get(f"{rota_plano}/comparacao")
    assert sem_setup.status_code == 200, sem_setup.text
    assert sem_setup.json() == {
        "planejamento": alterado.json(),
        "sugestao": sugestao,
        "setup": None,
    }


def test_comparacao_restrita_ao_planejador(cenario_ab):
    client, state, _, _, (op01, _, op03) = cenario_ab
    plano = _post(client, PLANOS, {"nome": "Manual", "ordens_ids": [op01, op03]})
    _post(client, SUGESTOES, {"ordens_ids": [op01, op03]})
    rota = f"{PLANOS}/{plano['id_planejamento']}/comparacao"
    client.cookies.clear()

    assert client.get(rota).status_code == 401

    _login(client, state.operator_email, state.password)
    resposta = client.get(rota)
    assert resposta.status_code == 403
    assert resposta.json() == {"detail": "Acesso não autorizado para este perfil."}
