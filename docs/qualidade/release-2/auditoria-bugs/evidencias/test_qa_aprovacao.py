"""Reprodução exploratória da R2. Um teste aprovado confirma o comportamento observado."""

import json
from uuid import UUID

import pytest
from sqlalchemy import text

from testes.integration.test_us13_sequencia_sugerida import SUGESTOES, _login, _post, cenario_ab
from testes.integration.test_us17_aprovacao import APROVACOES, CANDIDATOS


@pytest.mark.parametrize("alteracao", ["maquina-inativa", "compatibilidade-removida"])
def test_aprovacao_publica_maquina_que_deixou_de_ser_elegivel(cenario_ab, alteracao):
    client, state, _, _, (ordem_id, _, _) = cenario_ab
    dados = {"ordens_ids": [ordem_id]}
    fonte = _post(client, SUGESTOES, dados)
    sugestao_id = fonte["id_sugestao"]
    maquina = fonte["itens"][0]["maquina_id"]
    produto = client.get(f"/api/ordens-producao/{ordem_id}").json()["produto_id"]

    if alteracao == "maquina-inativa":
        alterada = client.patch(f"/api/maquinas/{maquina}/status", json={"ativo": False})
        assert alterada.json()["ativo"] is False
    else:
        alterada = client.put(f"/api/produtos/{produto}/maquinas", json={"maquinas_ids": []})
    assert alterada.status_code == 200, alterada.text

    nova_sugestao = client.post(SUGESTOES, json=dados)
    assert nova_sugestao.status_code == 422, nova_sugestao.text
    candidato = client.get(CANDIDATOS)
    assert candidato.status_code == 200
    assert any(item["origem_id"] == sugestao_id for item in candidato.json())
    assert client.get(APROVACOES).json() == []
    assert client.get(f"{SUGESTOES}/{sugestao_id}").json() == fonte

    aprovacao = client.post(APROVACOES, json={
        "origem": "sugerida", "origem_id": sugestao_id, **dados,
    })
    assert aprovacao.status_code == 201, aprovacao.text
    registrada = aprovacao.json()
    assert registrada["status"] == "APROVADO"
    assert registrada["itens"][0]["maquina_id"] == maquina
    with state.engine.connect() as db:
        id_persistido = db.scalar(text("""
            SELECT maquina_id FROM itens_aprovacao_planejamento WHERE ordem_id = :ordem
        """), {"ordem": UUID(ordem_id)})
    assert str(id_persistido) == maquina

    _login(client, state.operator_email, state.password)
    execucao = client.get(APROVACOES)
    assert execucao.status_code == 200
    assert execucao.json() == [registrada]
    print(json.dumps({
        "alteracao": alteracao,
        "alteracao_http": alterada.status_code,
        "nova_sugestao_http": nova_sugestao.status_code,
        "aprovacao_http": aprovacao.status_code,
        "execucao_http": execucao.status_code,
        "candidato_permaneceu_disponivel": True,
        "sugestao_historica_preservada": True,
        "maquina_inelegivel_persistida_e_exibida_ao_operador": True,
    }, ensure_ascii=False))
