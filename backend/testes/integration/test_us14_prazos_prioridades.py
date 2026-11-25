from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text


SUGESTOES = "/api/planejamentos/sugestoes"


def _post(client, rota, dados, **kwargs):
    resposta = client.post(rota, json=dados, **kwargs)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _ordem(client, codigo, familia_id, maquina_id):
    produto = _post(client, "/api/produtos", {
        "codigo": f"PROD-{codigo}", "nome": f"Produto {codigo}", "unidade": "un",
    })
    resposta = client.patch(
        f"/api/produtos/{produto['id_produto']}/familia",
        json={"family_id": familia_id},
    )
    assert resposta.status_code == 200, resposta.text

    resposta = client.put(
        f"/api/produtos/{produto['id_produto']}/maquinas",
        json={"maquinas_ids": [maquina_id]},
    )
    assert resposta.status_code == 200, resposta.text

    return _post(client, "/api/ordens-producao", {
        "codigo": codigo, "produto_id": produto["id_produto"], "quantidade": 10,
    }, headers={"Idempotency-Key": str(uuid4())})["id_ordem"]


def _planejar(client, ordem_id, prazo, prioridade, duracao=None):
    rota = f"/api/ordens-producao/{ordem_id}"
    resposta = client.put(rota, json={
        "prazo": prazo.isoformat(), "prioridade": prioridade,
    })
    assert resposta.status_code == 200, resposta.text

    if duracao is not None:
        resposta = client.patch(f"{rota}/duracao-estimada", json={
            "duracao_estimada_minutos": duracao,
        })
        assert resposta.status_code == 200, resposta.text


def _confirmar_persistencia(engine, sugestoes, itens):
    with engine.connect() as conexao:
        assert conexao.scalar(text("SELECT count(*) FROM sugestoes_planejamento")) == sugestoes
        assert conexao.scalar(text("SELECT count(*) FROM itens_sugestao_planejamento")) == itens


@pytest.fixture
def cenario_us14(seeded_auth, monkeypatch):
    from app.api.routes import sugestoes_planejamento

    # Mantém os prazos válidos na US08 e fixa o início da simulação.
    dia = date.today() + timedelta(days=2)

    class RelogioTeste(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.combine(dia, datetime.min.time(), tzinfo=tz).replace(hour=23)

    monkeypatch.setattr(sugestoes_planejamento, "datetime", RelogioTeste)

    client, state = seeded_auth.client, seeded_auth.state
    resposta = client.post("/api/auth/login", json={
        "email": state.email, "password": state.password,
    })
    assert resposta.status_code == 200, resposta.text

    a = _post(client, "/api/families", {"code": "A", "name": "Família A"})["id"]
    b = _post(client, "/api/families", {"code": "B", "name": "Família B"})["id"]
    maquina = _post(client, "/api/maquinas", {"codigo": "M01", "nome": "Máquina M01"})["id_maquina"]
    ordens = [_ordem(client, "OP01", a, maquina), _ordem(client, "OP02", a, maquina), _ordem(client, "OP03", b, maquina)]

    for origem, destino, minutos in ((a, b, 5), (b, a, 30)):
        _post(client, "/api/tempos-setup", {
            "familia_origem_id": origem,
            "familia_destino_id": destino,
            "tempo_setup_minutos": minutos,
        })

    return client, state, ordens, dia, maquina


def test_ordem_prioritaria_com_prazo_restritivo(cenario_us14):
    client, state, ordens, dia, maquina = cenario_us14
    op01, op02, op03 = ordens
    futuro = dia + timedelta(days=5)
    _planejar(client, op01, futuro, "Baixa", 30)
    _planejar(client, op02, futuro, "Média", 30)
    _planejar(client, op03, dia, "Alta", 40)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})

    assert sugestao["tempo_setup_original_minutos"] == 5
    assert sugestao["tempo_setup_total_minutos"] == 30
    assert sugestao["itens"] == [
        {"ordem_id": op03, "maquina_id": maquina, "posicao": 1, "posicao_original": 3, "setup_minutos": 0},
        {"ordem_id": op02, "maquina_id": maquina, "posicao": 2, "posicao_original": 2, "setup_minutos": 30},
        {"ordem_id": op01, "maquina_id": maquina, "posicao": 3, "posicao_original": 1, "setup_minutos": 0},
    ]
    consulta = client.get(f"{SUGESTOES}/{sugestao['id_sugestao']}")
    assert consulta.status_code == 200, consulta.text
    assert consulta.json() == sugestao
    _confirmar_persistencia(state.engine, 1, 3)


def test_prazo_influencia_ordens_de_mesma_prioridade(cenario_us14):
    client, _, (op01, op02, _), dia, _ = cenario_us14
    _planejar(client, op01, dia + timedelta(days=5), "Média", 40)
    _planejar(client, op02, dia, "Média", 40)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op02]})

    assert [item["ordem_id"] for item in sugestao["itens"]] == [op02, op01]
    assert sugestao["tempo_setup_total_minutos"] == 0


def test_prazo_mais_proximo_precede_setup_menor_quando_ambos_sao_viaveis(cenario_us14):
    client, _, (op01, _, op03), dia, _ = cenario_us14
    _planejar(client, op01, dia + timedelta(days=2), "Média", 40)
    _planejar(client, op03, dia + timedelta(days=1), "Média", 40)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op03]})

    assert [item["ordem_id"] for item in sugestao["itens"]] == [op03, op01]
    assert sugestao["tempo_setup_original_minutos"] == 5
    assert sugestao["tempo_setup_total_minutos"] == 30


def test_setup_menor_desempata_ordens_com_mesma_prioridade_e_prazo(cenario_us14):
    client, _, (op01, _, op03), dia, _ = cenario_us14
    prazo = dia + timedelta(days=1)
    _planejar(client, op01, prazo, "Média", 40)
    _planejar(client, op03, prazo, "Média", 40)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op03, op01]})

    assert [item["ordem_id"] for item in sugestao["itens"]] == [op01, op03]
    assert sugestao["tempo_setup_original_minutos"] == 30
    assert sugestao["tempo_setup_total_minutos"] == 5


@pytest.mark.parametrize("prazo_baixa_em_dias,setup_esperado", [(0, 30), (1, 5)])
def test_conflito_de_prazo_prioridade_e_setup(cenario_us14, prazo_baixa_em_dias, setup_esperado):
    client, state, (alta, _, baixa), dia, _ = cenario_us14
    _planejar(client, alta, dia + timedelta(days=1), "Alta", 40)
    _planejar(client, baixa, dia + timedelta(days=prazo_baixa_em_dias), "Baixa", 40)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [alta, baixa]})

    ordem_esperada = [baixa, alta] if prazo_baixa_em_dias == 0 else [alta, baixa]
    assert [item["ordem_id"] for item in sugestao["itens"]] == ordem_esperada
    assert sugestao["tempo_setup_original_minutos"] == 5
    assert sugestao["tempo_setup_total_minutos"] == setup_esperado
    _confirmar_persistencia(state.engine, 1, 2)


def test_prioridade_influencia_ordens_de_mesmo_prazo(cenario_us14):
    client, _, (op01, op02, _), dia, _ = cenario_us14
    prazo = dia + timedelta(days=5)
    _planejar(client, op01, prazo, "Baixa", 20)
    _planejar(client, op02, prazo, "Alta", 20)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op02]})

    assert [item["ordem_id"] for item in sugestao["itens"]] == [op02, op01]


def test_dados_incompletos_impedem_persistencia(cenario_us14):
    client, state, (op01, op02, _), dia, _ = cenario_us14
    _planejar(client, op01, dia, "Alta", 30)

    resposta = client.post(SUGESTOES, json={"ordens_ids": [op01, op02]})

    assert resposta.status_code == 422
    assert "A ordem OP02 está sem: prazo, prioridade, duração estimada." in resposta.json()["detail"]
    _confirmar_persistencia(state.engine, 0, 0)


def test_duracao_ausente_impede_persistencia(cenario_us14):
    client, state, (op01, _, _), dia, _ = cenario_us14
    _planejar(client, op01, dia, "Alta")

    resposta = client.post(SUGESTOES, json={"ordens_ids": [op01]})

    assert resposta.status_code == 422
    assert "A ordem OP01 está sem: duração estimada." in resposta.json()["detail"]
    _confirmar_persistencia(state.engine, 0, 0)


def test_prazo_e_prioridade_por_maquina_com_inicio_independente(cenario_us14):
    client, state, (op01, _, op03), dia, m1 = cenario_us14
    m2 = _post(client, "/api/maquinas", {"codigo": "M02", "nome": "Máquina M02"})["id_maquina"]
    c = _post(client, "/api/families", {"code": "C", "name": "Família C"})["id"]
    op04 = _ordem(client, "OP04", c, m2)
    op05 = _ordem(client, "OP05", c, m2)

    futuro = dia + timedelta(days=1)
    _planejar(client, op01, futuro, "Baixa", 30)
    _planejar(client, op03, dia, "Alta", 40)
    _planejar(client, op04, futuro, "Alta", 40)
    _planejar(client, op05, dia, "Baixa", 40)

    sugestao = _post(client, SUGESTOES, {
        "ordens_ids": [op01, op04, op03, op05],
    })

    assert sugestao["tempo_setup_original_minutos"] == 5
    assert sugestao["tempo_setup_total_minutos"] == 30
    assert [
        (item["ordem_id"], item["maquina_id"], item["setup_minutos"], item["posicao_original"])
        for item in sugestao["itens"]
    ] == [
        (op03, m1, 0, 3),
        (op01, m1, 30, 1),
        (op05, m2, 0, 4),
        (op04, m2, 0, 2),
    ]
    consulta = client.get(f"{SUGESTOES}/{sugestao['id_sugestao']}")
    assert consulta.status_code == 200, consulta.text
    assert consulta.json() == sugestao
    _confirmar_persistencia(state.engine, 1, 4)


def test_urgencia_incompleta_em_outra_maquina_impede_persistencia(cenario_us14):
    client, state, (op01, _, _), dia, _ = cenario_us14
    m2 = _post(client, "/api/maquinas", {"codigo": "M02", "nome": "Máquina M02"})["id_maquina"]
    c = _post(client, "/api/families", {"code": "C", "name": "Família C"})["id"]
    op04 = _ordem(client, "OP04", c, m2)
    _planejar(client, op01, dia, "Alta", 30)

    resposta = client.post(SUGESTOES, json={"ordens_ids": [op01, op04]})

    assert resposta.status_code == 422
    assert "A ordem OP04 está sem: prazo, prioridade, duração estimada." in resposta.json()["detail"]
    _confirmar_persistencia(state.engine, 0, 0)
