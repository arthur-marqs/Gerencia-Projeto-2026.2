"""Cenários complementares de regressão em banco descartável."""
import json
from uuid import UUID

import pytest
from sqlalchemy import text

from testes.integration.test_us13_sequencia_sugerida import (
    SUGESTOES, _login, _post, _setup, cenario_ab,
)

PLANOS = "/api/planejamentos"
APROVACOES = f"{PLANOS}/aprovacoes"
CANDIDATOS = f"{APROVACOES}/candidatos"


def registrar(record_property, **resultados):
    for nome, valor in resultados.items():
        record_property(nome, valor)
    print(json.dumps(resultados, ensure_ascii=False))


def test_fluxo_planejar_comparar_aprovar_consultar(cenario_ab, record_property):
    client, state, a, b, ordens = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    plano = _post(client, PLANOS, {"nome": "Ciclo Release 2", "ordens_ids": ordens})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})
    comparacao = client.get(f"{PLANOS}/{plano['id_planejamento']}/comparacao")
    assert comparacao.status_code == 200
    comparado = comparacao.json()
    assert comparado["planejamento"] == plano
    assert comparado["sugestao"] == sugestao
    assert comparado["setup"] == {
        "manual_minutos": 50, "sugerido_minutos": 20,
        "diferenca_minutos": -30, "referencia": "registrado",
    }
    ids_sugeridos = [ordens[0], ordens[2], ordens[1]]
    assert [item["ordem_id"] for item in sugestao["itens"]] == ids_sugeridos
    aprovacao = _post(client, APROVACOES, {
        "origem": "sugerida", "origem_id": sugestao["id_sugestao"],
        "ordens_ids": ids_sugeridos,
    })
    assert aprovacao["status"] == "APROVADO"
    assert [item["ordem_id"] for item in aprovacao["itens"]] == ids_sugeridos
    assert [item["maquina_id"] for item in aprovacao["itens"]] == [
        item["maquina_id"] for item in sugestao["itens"]
    ]
    with state.engine.connect() as banco:
        assert banco.scalar(text(
            "SELECT count(*) FROM itens_aprovacao_planejamento WHERE aprovacao_id = :id"
        ), {"id": UUID(aprovacao["id_aprovacao"])}) == 3
    _login(client, state.operator_email, state.password)
    consulta = client.get(APROVACOES)
    assert consulta.status_code == 200
    assert consulta.json() == [aprovacao]
    registrar(record_property, caso="RG-01", manual_min=50, sugerido_min=20,
              diferenca_min=-30, itens_persistidos=3, consulta_operador_http=200)


@pytest.mark.parametrize("alteracao", ["maquina-inativa", "vinculo-removido"])
def test_bug004_recusa_nova_aprovacao_desatualizada(cenario_ab, alteracao, record_property):
    client, state, _, _, (ordem, _, _) = cenario_ab
    fonte = _post(client, SUGESTOES, {"ordens_ids": [ordem]})
    sugestao_id = fonte["id_sugestao"]
    maquina = fonte["itens"][0]["maquina_id"]
    produto = client.get(f"/api/ordens-producao/{ordem}").json()["produto_id"]
    if alteracao == "maquina-inativa":
        escrita = client.patch(f"/api/maquinas/{maquina}/status", json={"ativo": False})
        assert escrita.json()["ativo"] is False
    else:
        escrita = client.put(f"/api/produtos/{produto}/maquinas", json={"maquinas_ids": []})
    assert escrita.status_code == 200
    candidatos = client.get(CANDIDATOS)
    assert candidatos.status_code == 200
    presente = any(item["origem_id"] == sugestao_id for item in candidatos.json())
    resposta = client.post(APROVACOES, json={
        "origem": "sugerida", "origem_id": sugestao_id, "ordens_ids": [ordem],
    })
    historico_preservado = client.get(f"{SUGESTOES}/{sugestao_id}").json() == fonte
    with state.engine.connect() as banco:
        aprovacoes = banco.scalar(text("SELECT count(*) FROM aprovacoes_planejamento"))
        itens = banco.scalar(text("SELECT count(*) FROM itens_aprovacao_planejamento"))
    _login(client, state.operator_email, state.password)
    operador = client.get(APROVACOES)
    assert operador.status_code == 200
    publicados = len(operador.json())
    registrar(record_property, caso="BUG-004", alteracao=alteracao, candidato_presente=presente,
              aprovacao_http=resposta.status_code, aprovacoes=aprovacoes, itens=itens,
              publicados_operador=publicados, historico_preservado=historico_preservado)
    assert (presente, resposta.status_code, aprovacoes, itens, publicados, historico_preservado) == (
        False, 409, 0, 0, 0, True
    )
    assert "Gere uma sequência sugerida atualizada" in resposta.json()["detail"]
