from uuid import uuid4

import pytest
from sqlalchemy import text


SUGESTOES = "/api/planejamentos/sugestoes"


def _login(client, email, senha):
    resposta = client.post("/api/auth/login", json={"email": email, "password": senha})
    assert resposta.status_code == 200, resposta.text


def _post(client, rota, dados, **kwargs):
    resposta = client.post(rota, json=dados, **kwargs)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _ordem(client, codigo, familia_id=None):
    produto = _post(client, "/api/produtos", {
        "codigo": f"PROD-{codigo}", "nome": f"Produto {codigo}", "unidade": "un",
    })
    if familia_id is not None:
        resposta = client.patch(
            f"/api/produtos/{produto['id_produto']}/familia", json={"family_id": familia_id}
        )
        assert resposta.status_code == 200, resposta.text

    return _post(client, "/api/ordens-producao", {
        "codigo": codigo, "produto_id": produto["id_produto"], "quantidade": 10,
    }, headers={"Idempotency-Key": str(uuid4())})


def _setup(client, origem, destino, minutos):
    _post(client, "/api/tempos-setup", {
        "familia_origem_id": origem,
        "familia_destino_id": destino,
        "tempo_setup_minutos": minutos,
    })


def _confirmar_sugestoes_salvas(engine, sugestoes, itens):
    with engine.connect() as conexao:
        assert conexao.scalar(text("SELECT count(*) FROM sugestoes_planejamento")) == sugestoes
        assert conexao.scalar(text("SELECT count(*) FROM itens_sugestao_planejamento")) == itens


@pytest.fixture
def cenario_ab(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    _login(client, state.email, state.password)
    a = _post(client, "/api/families", {"code": "A", "name": "Família A"})["id"]
    b = _post(client, "/api/families", {"code": "B", "name": "Família B"})["id"]
    ordens = [
        _ordem(client, "OP01", a)["id_ordem"],
        _ordem(client, "OP02", b)["id_ordem"],
        _ordem(client, "OP03", a)["id_ordem"],
    ]
    return client, state, a, b, ordens


def test_reduz_setup_direcional_sem_planejamento_manual(cenario_ab):
    client, state, a, b, ordens = cenario_ab
    op01, op02, op03 = ordens
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": ordens})

    assert sugestao["tempo_setup_original_minutos"] == 50
    assert sugestao["tempo_setup_total_minutos"] == 20
    assert sugestao["itens"] == [
        {"ordem_id": op01, "posicao": 1, "posicao_original": 1, "setup_minutos": 0},
        {"ordem_id": op03, "posicao": 2, "posicao_original": 3, "setup_minutos": 0},
        {"ordem_id": op02, "posicao": 3, "posicao_original": 2, "setup_minutos": 20},
    ]
    consulta = client.get(f"{SUGESTOES}/{sugestao['id_sugestao']}")
    assert consulta.status_code == 200
    assert consulta.json() == sugestao
    assert client.get("/api/planejamentos").json() == []
    _confirmar_sugestoes_salvas(state.engine, 1, 3)


def test_retorna_pendencias_e_so_persiste_depois_da_correcao(cenario_ab):
    client, state, a, b, ordens = cenario_ab
    _setup(client, a, b, 20)
    ordem_sem_familia = _ordem(client, "OP04")
    selecionadas = [*ordens, ordem_sem_familia["id_ordem"]]

    resposta = client.post(SUGESTOES, json={"ordens_ids": selecionadas})
    assert resposta.status_code == 422
    detalhe = resposta.json()["detail"]
    assert "A ordem OP04 usa o produto PROD-OP04 (Produto OP04)" in detalhe
    assert "sem família associada" in detalhe
    assert "B → A sem cadastro" in detalhe
    assert "A → B" not in detalhe
    _confirmar_sugestoes_salvas(state.engine, 0, 0)

    resposta = client.patch(
        f"/api/produtos/{ordem_sem_familia['produto_id']}/familia",
        json={"family_id": a},
    )
    assert resposta.status_code == 200, resposta.text
    resposta = client.post(SUGESTOES, json={"ordens_ids": selecionadas})
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Tempo de setup de B → A sem cadastro."
    _confirmar_sugestoes_salvas(state.engine, 0, 0)

    _setup(client, b, a, 30)
    sugestao = _post(client, SUGESTOES, {"ordens_ids": selecionadas})
    assert sugestao["tempo_setup_total_minutos"] == 20
    _confirmar_sugestoes_salvas(state.engine, 1, 4)


def test_reduz_setup_direcional_com_tres_familias(cenario_ab):
    client, state, a, b, (op01, op02, op03) = cenario_ab
    c = _post(client, "/api/families", {"code": "C", "name": "Família C"})["id"]
    op04 = _ordem(client, "OP04", c)["id_ordem"]
    for origem, destino, minutos in (
        (a, b, 20), (a, c, 30), (b, a, 4), (b, c, 15), (c, a, 25), (c, b, 3),
    ):
        _setup(client, origem, destino, minutos)

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op02, op03, op04]})

    assert sugestao["tempo_setup_original_minutos"] == 54
    assert sugestao["tempo_setup_total_minutos"] == 7
    assert [item["ordem_id"] for item in sugestao["itens"]] == [op04, op02, op01, op03]
    assert [item["setup_minutos"] for item in sugestao["itens"]] == [0, 3, 4, 0]
    _confirmar_sugestoes_salvas(state.engine, 1, 4)


def test_ordem_nao_pendente_bloqueia_a_geracao_sem_persistencia(cenario_ab):
    client, state, a, b, (op01, op02, _) = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    with state.engine.begin() as conexao:
        conexao.execute(
            text("UPDATE ordens_producao SET status = 'CONCLUIDA' WHERE id_ordem = :id"),
            {"id": op02},
        )

    resposta = client.post(SUGESTOES, json={"ordens_ids": [op01, op02]})

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Somente ordens pendentes podem ser planejadas."
    _confirmar_sugestoes_salvas(state.engine, 0, 0)


@pytest.mark.parametrize("tempo_reverso", [20, 30])
def test_preserva_ordem_quando_as_alternativas_sao_iguais_ou_piores(cenario_ab, tempo_reverso):
    client, _, a, b, (op01, op02, op03) = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, tempo_reverso)
    selecionadas = [op03, op01, op02]

    sugestao = _post(client, SUGESTOES, {"ordens_ids": selecionadas})

    assert [item["ordem_id"] for item in sugestao["itens"]] == selecionadas
    assert sugestao["tempo_setup_original_minutos"] == sugestao["tempo_setup_total_minutos"] == 20


def test_recupera_sugestao_do_mesmo_conjunto_e_preserva_planejamento_manual(cenario_ab):
    client, state, a, b, (op01, op02, op03) = cenario_ab
    _setup(client, a, b, 20)
    _setup(client, b, a, 30)
    planejamento = _post(client, "/api/planejamentos", {
        "nome": "Planejamento manual", "ordens_ids": [op02, op03, op01],
    })
    rota_planejamento = f"/api/planejamentos/{planejamento['id_planejamento']}"
    assert client.get(f"{rota_planejamento}/sugestao").status_code == 404

    _post(client, SUGESTOES, {"ordens_ids": [op02, op03, op01]})
    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01, op02, op03]})
    _post(client, SUGESTOES, {"ordens_ids": [op01, op02]})
    op04 = _ordem(client, "OP04", a)["id_ordem"]
    _post(client, SUGESTOES, {"ordens_ids": [op01, op02, op03, op04]})

    consulta = client.get(f"{rota_planejamento}/sugestao")
    assert consulta.status_code == 200
    assert consulta.json() == sugestao
    assert client.get(rota_planejamento).json() == planejamento
    _confirmar_sugestoes_salvas(state.engine, 4, 12)


def test_ordem_unica_tem_setup_zero_sem_tempos_cadastrados(cenario_ab):
    client, _, _, _, (op01, _, _) = cenario_ab

    sugestao = _post(client, SUGESTOES, {"ordens_ids": [op01]})

    assert sugestao["tempo_setup_total_minutos"] == 0
    assert sugestao["itens"] == [
        {"ordem_id": op01, "posicao": 1, "posicao_original": 1, "setup_minutos": 0},
    ]


def test_rejeita_selecao_vazia_duplicada_ou_inexistente(cenario_ab):
    client, state, _, _, (op01, _, _) = cenario_ab

    vazia = client.post(SUGESTOES, json={"ordens_ids": []})
    assert vazia.status_code == 422
    assert "Selecione pelo menos uma ordem" in vazia.json()["detail"]

    duplicada = client.post(SUGESTOES, json={"ordens_ids": [op01, op01]})
    assert duplicada.status_code == 422
    assert "apenas uma vez" in duplicada.json()["detail"]

    inexistente = client.post(SUGESTOES, json={"ordens_ids": [op01, str(uuid4())]})
    assert inexistente.status_code == 404
    _confirmar_sugestoes_salvas(state.engine, 0, 0)


def test_geracao_e_consulta_exigem_sessao_de_planejador(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert client.post(SUGESTOES, json={"ordens_ids": []}).status_code == 401

    _login(client, state.operator_email, state.password)
    assert client.post(SUGESTOES, json={"ordens_ids": []}).status_code == 403
    assert client.get(f"{SUGESTOES}/{uuid4()}").status_code == 403
    assert client.get(f"/api/planejamentos/{uuid4()}/sugestao").status_code == 403
    _confirmar_sugestoes_salvas(state.engine, 0, 0)
