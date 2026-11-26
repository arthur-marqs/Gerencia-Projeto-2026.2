from concurrent.futures import ThreadPoolExecutor
from time import monotonic, sleep
from uuid import uuid4

import pytest
from sqlalchemy import text

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
SUGESTAO_INDISPONIVEL = (
    "A sugestão ficou indisponível para aprovação. "
    "Gere uma sequência sugerida atualizada."
)


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


@pytest.mark.parametrize("alteracao", ["maquina-inativa", "compatibilidade-removida", "sugestao-legada"])
def test_recusa_sugestao_com_maquina_inelegivel_sem_alterar_historico(cenario_ab, alteracao):
    client, state, _, _, (op01, _, op03) = cenario_ab
    dados = {"ordens_ids": [op01, op03]}
    sugestao = _post(client, SUGESTOES, dados)
    sugestao_id = sugestao["id_sugestao"]
    rota_sugestao = f"{SUGESTOES}/{sugestao_id}"
    maquina_id = sugestao["itens"][0]["maquina_id"]
    produto_id = client.get(f"/api/ordens-producao/{op01}").json()["produto_id"]
    assert [item["origem_id"] for item in client.get(CANDIDATOS).json()] == [sugestao_id]

    if alteracao == "maquina-inativa":
        resposta = client.patch(f"/api/maquinas/{maquina_id}/status", json={"ativo": False})
        assert resposta.status_code == 200 and resposta.json()["ativo"] is False
    elif alteracao == "compatibilidade-removida":
        resposta = client.put(f"/api/produtos/{produto_id}/maquinas", json={"maquinas_ids": []})
        assert resposta.status_code == 200 and resposta.json()["maquinas_compativeis"] == []
    else:
        # Sugestões persistidas antes da US15 podem ter máquina nula.
        with state.engine.begin() as db:
            db.execute(text("""
                UPDATE itens_sugestao_planejamento SET maquina_id = NULL
                WHERE sugestao_id = :sugestao_id AND ordem_id = :ordem_id
            """), {"sugestao_id": sugestao_id, "ordem_id": op01})

    historico = client.get(rota_sugestao).json()
    if alteracao != "sugestao-legada":
        assert historico == sugestao
        assert client.post(SUGESTOES, json=dados).status_code == 422
    else:
        assert historico["itens"][0]["maquina_id"] is None

    candidatos = client.get(CANDIDATOS)
    resposta = client.post(APROVACOES, json={"origem": "sugerida", "origem_id": sugestao_id, **dados})
    assert (candidatos.status_code, candidatos.json(), resposta.status_code) == (200, [], 409)
    assert resposta.json() == {"detail": SUGESTAO_INDISPONIVEL}
    assert client.get(rota_sugestao).json() == historico
    with state.engine.connect() as db:
        assert db.scalar(text("SELECT count(*) FROM aprovacoes_planejamento")) == 0
        assert db.scalar(text("SELECT count(*) FROM itens_aprovacao_planejamento")) == 0

    _login(client, state.operator_email, state.password)
    execucao = client.get(APROVACOES)
    assert execucao.status_code == 200 and execucao.json() == []


def test_repeticao_preserva_aprovacao_existente_apos_inativar_maquina(cenario_ab):
    client, _, _, _, (op01, _, _) = cenario_ab
    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01]})
    pedido = {"origem": "sugerida", "origem_id": sugestao["id_sugestao"]}
    aprovada = _post(client, APROVACOES, pedido)
    maquina_id = sugestao["itens"][0]["maquina_id"]
    assert client.patch(f"/api/maquinas/{maquina_id}/status", json={"ativo": False}).status_code == 200

    repetida = client.post(APROVACOES, json=pedido)
    assert repetida.status_code == 200 and repetida.json() == aprovada
    assert client.get(APROVACOES).json() == [aprovada]


@pytest.mark.parametrize("alteracao", ["maquina-inativa", "compatibilidade-removida"])
def test_nova_aprovacao_aguarda_alteracao_de_elegibilidade_em_curso(cenario_ab, alteracao):
    client, state, _, _, (op01, _, _) = cenario_ab
    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01]})
    pedido = {"origem": "sugerida", "origem_id": sugestao["id_sugestao"]}
    maquina_id = sugestao["itens"][0]["maquina_id"]
    produto_id = client.get(f"/api/ordens-producao/{op01}").json()["produto_id"]

    aguardou = False
    with ThreadPoolExecutor(max_workers=1) as executor:
        with state.engine.begin() as db, state.engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as monitor:
            bloqueador = db.scalar(text("SELECT pg_backend_pid()"))
            if alteracao == "maquina-inativa":
                db.execute(text("UPDATE maquinas SET ativo = false WHERE id_maquina = :maquina"),
                           {"maquina": maquina_id})
            else:
                db.execute(text("""
                    DELETE FROM produto_maquina WHERE id_produto = :produto AND id_maquina = :maquina
                """), {"produto": produto_id, "maquina": maquina_id})
            requisicao = executor.submit(client.post, APROVACOES, json=pedido)

            limite = monotonic() + 5
            while not requisicao.done() and monotonic() < limite:
                aguardou = monitor.scalar(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_stat_activity
                        WHERE :bloqueador = ANY(pg_blocking_pids(pid))
                    )
                """), {"bloqueador": bloqueador})
                if aguardou:
                    break
                sleep(0.02)
        resposta = requisicao.result(timeout=10)

    assert aguardou, (resposta.status_code, resposta.json())
    assert resposta.status_code == 409 and resposta.json() == {"detail": SUGESTAO_INDISPONIVEL}
    assert client.get(APROVACOES).json() == []


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
