"""Sondagem de QA em banco descartável com dados válidos para CT-130 a CT-132."""

from hashlib import sha256
from json import dumps

import pytest

from testes.integration.drivers.test_driver04_controle_acesso import _snapshot_banco
from testes.integration.test_us13_sequencia_sugerida import _login, _post, _setup, cenario_ab


MAQUINAS = "/api/maquinas"
SETUPS = "/api/tempos-setup"
PLANOS = "/api/planejamentos"
SUGESTOES = f"{PLANOS}/sugestoes"


@pytest.fixture
def matriz(cenario_ab):
    client, state, a, b, ordens = cenario_ab
    c = _post(client, "/api/families", {"code": "C", "name": "Família C"})["id"]
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    livre = _post(client, MAQUINAS, {"codigo": "M02", "nome": "Máquina sem vínculos"})["id_maquina"]
    maquinas = client.get(MAQUINAS).json()
    m01 = next(maquina["id_maquina"] for maquina in maquinas if maquina["codigo"] == "M01")
    plano = _post(client, PLANOS, {"nome": "Plano QA Driver04", "ordens_ids": ordens})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})
    plano_id = plano["id_planejamento"]
    sugestao_id = sugestao["id_sugestao"]

    return client, state, {
        "listar-maquinas": ("GET", MAQUINAS, None, 200),
        "cadastrar-maquina": ("POST", MAQUINAS, {"codigo": "MQA", "nome": "Máquina QA"}, 201),
        "editar-maquina": ("PUT", f"{MAQUINAS}/{m01}", {"codigo": "M01", "nome": "Máquina QA editada"}, 200),
        "alterar-status-maquina": ("PATCH", f"{MAQUINAS}/{m01}/status", {"ativo": False}, 200),
        "excluir-maquina-livre": ("DELETE", f"{MAQUINAS}/{livre}", None, 204),
        "listar-setups": ("GET", SETUPS, None, 200),
        "cadastrar-setup": ("POST", SETUPS, {
            "familia_origem_id": a, "familia_destino_id": c, "tempo_setup_minutos": 15,
        }, 201),
        "gerar-sugestao": ("POST", SUGESTOES, {"ordens_ids": ordens}, 201),
        "consultar-sugestao": ("GET", f"{SUGESTOES}/{sugestao_id}", None, 200),
        "comparar-sequencias": ("GET", f"{PLANOS}/{plano_id}/comparacao", None, 200),
        "consultar-plano": ("GET", f"{PLANOS}/{plano_id}", None, 200),
        "reordenar-manual": ("PUT", f"{PLANOS}/{plano_id}", {
            "nome": "Plano QA Driver04", "ordens_ids": list(reversed(ordens)),
        }, 200),
    }


def _impressao_digital_do_banco(engine):
    snapshot = _snapshot_banco(engine)
    return sha256(dumps(snapshot, sort_keys=True).encode()).hexdigest()


@pytest.mark.parametrize("operacao", [
    "listar-maquinas", "cadastrar-maquina", "editar-maquina", "alterar-status-maquina",
    "excluir-maquina-livre", "listar-setups", "cadastrar-setup", "gerar-sugestao",
    "consultar-sugestao", "comparar-sequencias", "consultar-plano", "reordenar-manual",
])
@pytest.mark.parametrize("perfil,caso,negacao,mensagem", [
    pytest.param("operador", "CT-130", 403, "Acesso não autorizado para este perfil.", id="CT-130"),
    pytest.param("sem-sessao", "CT-131", 401, "Sessão inválida ou expirada.", id="CT-131"),
    pytest.param("planejador", "CT-132", None, None, id="CT-132"),
])
def test_matriz_driver04(matriz, operacao, perfil, caso, negacao, mensagem, record_property):
    client, state, operacoes = matriz
    metodo, caminho, dados, status_autorizado = operacoes[operacao]
    if perfil == "operador":
        _login(client, state.operator_email, state.password)
    elif perfil == "sem-sessao":
        client.cookies.clear()

    antes = _impressao_digital_do_banco(state.engine)
    resposta = client.request(metodo, caminho, **({"json": dados} if dados is not None else {}))
    mudou = _impressao_digital_do_banco(state.engine) != antes

    record_property("caso", caso)
    record_property("operacao", operacao)
    record_property("http", resposta.status_code)
    record_property("banco_alterado", mudou)
    assert resposta.status_code == (negacao or status_autorizado), resposta.text
    if negacao is not None:
        assert resposta.json() == {"detail": mensagem}
        assert not mudou
    else:
        if status_autorizado != 204:
            assert resposta.json()
        assert mudou == (metodo != "GET")
