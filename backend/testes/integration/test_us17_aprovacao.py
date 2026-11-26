from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest

from testes.integration.test_us13_sequencia_sugerida import (
    SUGESTOES,
    _login,
    _post,
    _setup,
    cenario_ab,
)

PLANOS = "/api/planejamentos"
APROVACOES = f"{PLANOS}/aprovacoes"
CANDIDATOS = f"{APROVACOES}/candidatos"


def _alternativas(client, a, b, ordens):
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    plano = _post(client, PLANOS, {"nome": "Plano US17", "ordens_ids": ordens})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})
    return plano, sugestao


@pytest.mark.parametrize("origem", ["manual", "sugerida"])
def test_aprova_somente_a_alternativa_escolhida_e_publica_para_execucao(cenario_ab, origem):
    client, state, a, b, (op01, op02, op03) = cenario_ab
    plano, sugestao = _alternativas(client, a, b, [op01, op02, op03])
    id_plano = plano["id_planejamento"]
    id_sugestao = sugestao["id_sugestao"]

    consulta = client.get(CANDIDATOS)
    assert consulta.status_code == 200, consulta.text
    candidatos = {item["origem"]: item for item in consulta.json()}
    assert set(candidatos) == {"manual", "sugerida"}
    assert candidatos["manual"]["origem_id"] == id_plano
    assert candidatos["sugerida"]["origem_id"] == id_sugestao
    assert [item["ordem_id"] for item in candidatos["manual"]["itens"]] == [op01, op02, op03]
    assert [item["ordem_id"] for item in candidatos["sugerida"]["itens"]] == [op01, op03, op02]
    escolhido = candidatos[origem]
    outra = candidatos["sugerida" if origem == "manual" else "manual"]
    pedido = {
        "origem": origem,
        "origem_id": escolhido["origem_id"],
        "ordens_ids": [item["ordem_id"] for item in escolhido["itens"]],
    }

    aprovado = _post(client, APROVACOES, pedido)

    assert aprovado["status"] == "APROVADO"
    assert aprovado["aprovado_por"] == str(state.user_id)
    assert aprovado["aprovado_em"]
    for campo in ("origem", "origem_id", "nome", "itens"):
        assert aprovado[campo] == escolhido[campo]
    assert client.get(APROVACOES).json() == [aprovado]
    assert client.get(f"{PLANOS}/{id_plano}").json() == plano
    assert client.get(f"{SUGESTOES}/{id_sugestao}").json() == sugestao
    assert client.get(CANDIDATOS).json() == []

    repetida = client.post(APROVACOES, json=pedido)
    assert repetida.status_code == 200
    assert repetida.json() == aprovado
    conflito = client.post(APROVACOES, json={"origem": outra["origem"], "origem_id": outra["origem_id"]})
    assert conflito.status_code == 409
    assert client.get(APROVACOES).json() == [aprovado]

    _login(client, state.operator_email, state.password)
    execucao = client.get(APROVACOES)
    assert execucao.status_code == 200
    assert execucao.json() == [aprovado]
    assert client.get(CANDIDATOS).status_code == 403
    assert client.post(APROVACOES, json=pedido).status_code == 403


def test_informa_ausencia_e_nao_registra_aprovacao(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    _login(client, state.email, state.password)

    assert client.get(CANDIDATOS).json() == []
    for pedido in ({}, {"origem": "manual", "origem_id": str(uuid4())}):
        resposta = client.post(APROVACOES, json=pedido)
        assert resposta.status_code == 404, resposta.text
        assert resposta.json() == {"detail": "Não existe planejamento disponível para aprovação."}
    assert client.get(APROVACOES).json() == []


def test_rejeita_sequencia_desatualizada_e_preserva_manual_aprovado(cenario_ab):
    client, _, _, _, (op01, _, op03) = cenario_ab
    plano = _post(client, PLANOS, {"nome": "Plano", "ordens_ids": [op01, op03]})
    id_plano = plano["id_planejamento"]
    rota_plano = f"{PLANOS}/{id_plano}"
    atual = {"nome": "Plano", "ordens_ids": [op03, op01]}
    assert client.put(rota_plano, json=atual).status_code == 200

    pedido = {"origem": "manual", "origem_id": id_plano, "ordens_ids": [op01, op03]}
    resposta = client.post(APROVACOES, json=pedido)
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "A sequência mudou. Atualize a lista antes de aprovar."
    assert client.get(APROVACOES).json() == []

    aprovado = _post(client, APROVACOES, {**pedido, "ordens_ids": atual["ordens_ids"]})
    assert client.put(rota_plano, json={"nome": "Alterado", "ordens_ids": [op01]}).status_code == 409
    assert client.get(APROVACOES).json() == [aprovado]
    assert [item["ordem_id"] for item in aprovado["itens"]] == [op03, op01]


def test_sugestao_independente_pode_ser_aprovada(cenario_ab):
    client, _, _, _, (op01, _, op03) = cenario_ab
    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op03]})
    assert client.get(PLANOS).json() == []

    aprovado = _post(client, APROVACOES, {"origem": "sugerida", "origem_id": sugestao["id_sugestao"]})

    assert [item["codigo_ordem"] for item in aprovado["itens"]] == ["OP01", "OP03"]
    assert all(item["codigo_maquina"] == "M01" for item in aprovado["itens"])


def test_aprovacoes_concorrentes_nao_alocam_a_mesma_ordem_duas_vezes(cenario_ab):
    client, _, a, b, ordens = cenario_ab
    plano, sugestao = _alternativas(client, a, b, ordens)
    pedidos = [
        {"origem": "manual", "origem_id": plano["id_planejamento"]},
        {"origem": "sugerida", "origem_id": sugestao["id_sugestao"]},
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(lambda pedido: client.post(APROVACOES, json=pedido), pedidos))

    assert sorted(resposta.status_code for resposta in respostas) == [201, 409]
    aprovada = next(resposta.json() for resposta in respostas if resposta.status_code == 201)
    assert client.get(APROVACOES).json() == [aprovada]
    assert {item["ordem_id"] for item in aprovada["itens"]} == set(ordens)


def test_aprovacao_e_execucao_exigem_sessao(client):
    assert client.get(CANDIDATOS).status_code == 401
    assert client.get(APROVACOES).status_code == 401
    assert client.post(APROVACOES, json={}).status_code == 401
