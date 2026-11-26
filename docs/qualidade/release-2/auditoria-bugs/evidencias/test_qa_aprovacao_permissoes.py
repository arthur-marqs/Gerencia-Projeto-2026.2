"""Complemento avulso à matriz do Driver04 para as operações da US17."""

import pytest
from sqlalchemy import text

from testes.integration.test_us13_sequencia_sugerida import SUGESTOES, _login, _post, cenario_ab
from testes.integration.test_us17_aprovacao import APROVACOES, CANDIDATOS


@pytest.mark.parametrize("perfil,http_esperado", [("operador", 403), ("sem-sessao", 401), ("planejador", 200)])
@pytest.mark.parametrize("operacao", ["listar-candidatos", "aprovar-sugestao"])
def test_qa_acesso_aprovacao_com_sugestao_disponivel(cenario_ab, perfil, http_esperado, operacao):
    client, state, _, _, (ordem_id, _, _) = cenario_ab
    fonte = _post(client, SUGESTOES, {"ordens_ids": [ordem_id]})
    dados = {"origem": "sugerida", "origem_id": fonte["id_sugestao"], "ordens_ids": [ordem_id]}

    def estado():
        with state.engine.connect() as db:
            return tuple(db.execute(text(f"SELECT * FROM {tabela} ORDER BY 1")).all() for tabela in (
                "ordens_producao", "sugestoes_planejamento", "itens_sugestao_planejamento",
                "aprovacoes_planejamento", "itens_aprovacao_planejamento",
            ))

    if perfil == "operador":
        _login(client, state.operator_email, state.password)
    elif perfil == "sem-sessao":
        client.cookies.clear()

    antes = estado()
    escrita = operacao == "aprovar-sugestao"
    resposta = client.post(APROVACOES, json=dados) if escrita else client.get(CANDIDATOS)
    if perfil != "planejador":
        assert resposta.status_code == http_esperado
        assert set(resposta.json()) == {"detail"}
        assert estado() == antes
    elif escrita:
        assert resposta.status_code == 201
        depois = estado()
        assert depois[:3] == antes[:3]
        assert len(depois[3]) == len(depois[4]) == 1
    else:
        assert resposta.status_code == http_esperado
        assert resposta.json()[0]["origem_id"] == fonte["id_sugestao"]
        assert estado() == antes
