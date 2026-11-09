
from uuid import uuid4

from sqlalchemy import text


def _login(client, email, senha):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": senha},
    )


def _criar_ordens(client):
    produto = client.post(
        "/api/produtos",
        json={
            "codigo": "PRD-US12",
            "nome": "Produto US12",
            "unidade": "un",
        },
    )
    assert produto.status_code == 201, produto.text

    ordens_ids = []

    for numero in range(1, 4):
        resposta = client.post(
            "/api/ordens-producao",
            json={
                "codigo": f"OP-US12-{numero}",
                "produto_id": produto.json()["id_produto"],
                "quantidade": 10,
            },
        )
        assert resposta.status_code == 201, resposta.text
        ordens_ids.append(resposta.json()["id_ordem"])

    return ordens_ids


def _criar_planejamento(client, ordens_ids, nome="Planejamento US12"):
    return client.post(
        "/api/planejamentos",
        json={"nome": nome, "ordens_ids": ordens_ids},
    )


def test_planejador_cria_planejamento_com_sequencia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)
    sequencia = [ordens_ids[2], ordens_ids[0], ordens_ids[1]]

    resposta = _criar_planejamento(client, sequencia)

    assert resposta.status_code == 201, resposta.text
    dados = resposta.json()
    assert dados["nome"] == "Planejamento US12"
    assert dados["criado_por"] == str(state.user_id)
    assert [item["ordem_id"] for item in dados["itens"]] == sequencia
    assert [item["posicao"] for item in dados["itens"]] == [1, 2, 3]


def test_planejamento_persiste_no_banco(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)
    resposta = _criar_planejamento(client, ordens_ids)
    assert resposta.status_code == 201, resposta.text

    planejamento_id = resposta.json()["id_planejamento"]

    with state.engine.connect() as conexao:
        itens = conexao.execute(
            text(
                """
                SELECT ordem_id, posicao
                FROM itens_planejamento
                WHERE planejamento_id = :id
                ORDER BY posicao
                """
            ),
            {"id": planejamento_id},
        ).all()

    assert [str(item.ordem_id) for item in itens] == ordens_ids
    assert [item.posicao for item in itens] == [1, 2, 3]


def test_planejador_lista_e_consulta_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)
    resposta = _criar_planejamento(client, ordens_ids)
    assert resposta.status_code == 201, resposta.text

    planejamento_id = resposta.json()["id_planejamento"]

    consulta = client.get(f"/api/planejamentos/{planejamento_id}")
    assert consulta.status_code == 200
    assert consulta.json()["id_planejamento"] == planejamento_id

    listagem = client.get("/api/planejamentos")
    assert listagem.status_code == 200
    assert any(
        item["id_planejamento"] == planejamento_id
        for item in listagem.json()
    )


def test_nao_permite_planejamento_sem_ordens(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    resposta = _criar_planejamento(client, [])

    assert resposta.status_code == 422


def test_nao_permite_ordens_duplicadas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)

    resposta = _criar_planejamento(
        client, [ordens_ids[0], ordens_ids[0]]
    )

    assert resposta.status_code == 422


def test_nao_permite_ordem_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    resposta = _criar_planejamento(client, [str(uuid4())])

    assert resposta.status_code == 404


def test_nao_permite_ordem_nao_pendente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)

    with state.engine.begin() as conexao:
        conexao.execute(
            text(
                """
                UPDATE ordens_producao
                SET status = 'CONCLUIDA'
                WHERE id_ordem = :id
                """
            ),
            {"id": ordens_ids[0]},
        )

    resposta = _criar_planejamento(client, [ordens_ids[0]])

    assert resposta.status_code == 422


def test_planejamento_exige_autenticacao(seeded_auth):
    resposta = _criar_planejamento(
        seeded_auth.client, [str(uuid4())]
    )

    assert resposta.status_code == 401


def test_operador_nao_pode_criar_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(
        client, state.operator_email, state.password
    ).status_code == 200

    resposta = _criar_planejamento(client, [str(uuid4())])

    assert resposta.status_code == 403


def test_consulta_planejamento_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    resposta = client.get(f"/api/planejamentos/{uuid4()}")

    assert resposta.status_code == 404


def test_nao_permite_ordem_em_dois_planejamentos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)

    primeiro = _criar_planejamento(
        client,
        [ordens_ids[0], ordens_ids[1]],
        nome="Planejamento A",
    )
    assert primeiro.status_code == 201, primeiro.text

    segundo = _criar_planejamento(
        client,
        [ordens_ids[0], ordens_ids[2]],
        nome="Planejamento B",
    )

    assert segundo.status_code == 409

    listagem = client.get("/api/planejamentos")
    assert listagem.status_code == 200
    assert len(listagem.json()) == 1


def test_planejador_altera_sequencia_do_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)

    criacao = _criar_planejamento(client, ordens_ids[:2])
    assert criacao.status_code == 201, criacao.text

    planejamento_id = criacao.json()["id_planejamento"]

    nova_sequencia = [
        ordens_ids[1],
        ordens_ids[2],
        ordens_ids[0],
    ]

    resposta = client.put(
        f"/api/planejamentos/{planejamento_id}",
        json={
            "nome": "Planejamento atualizado",
            "ordens_ids": nova_sequencia,
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "Planejamento atualizado"
    assert [item["ordem_id"] for item in resposta.json()["itens"]] == nova_sequencia
    assert [item["posicao"] for item in resposta.json()["itens"]] == [1, 2, 3]

    consulta = client.get(f"/api/planejamentos/{planejamento_id}")
    assert consulta.status_code == 200
    assert [item["ordem_id"] for item in consulta.json()["itens"]] == nova_sequencia


def test_atualizacao_remove_ordem_do_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)
    criacao = _criar_planejamento(client, ordens_ids)
    assert criacao.status_code == 201, criacao.text

    planejamento_id = criacao.json()["id_planejamento"]

    resposta = client.put(
        f"/api/planejamentos/{planejamento_id}",
        json={
            "nome": "Planejamento reduzido",
            "ordens_ids": [ordens_ids[2], ordens_ids[0]],
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert [item["ordem_id"] for item in resposta.json()["itens"]] == [
        ordens_ids[2],
        ordens_ids[0],
    ]
    assert [item["posicao"] for item in resposta.json()["itens"]] == [1, 2]

def test_atualizacao_rejeita_lista_vazia(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)
    criacao = _criar_planejamento(client, [ordens_ids[0]])
    assert criacao.status_code == 201, criacao.text

    planejamento_id = criacao.json()["id_planejamento"]

    resposta = client.put(
        f"/api/planejamentos/{planejamento_id}",
        json={"nome": "Planejamento vazio", "ordens_ids": []},
    )

    assert resposta.status_code == 422

    consulta = client.get(f"/api/planejamentos/{planejamento_id}")
    assert [item["ordem_id"] for item in consulta.json()["itens"]] == [
        ordens_ids[0]
    ]

def test_atualizacao_rejeita_ordem_de_outro_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    ordens_ids = _criar_ordens(client)

    primeiro = _criar_planejamento(
        client, [ordens_ids[0]], nome="Planejamento A"
    )
    segundo = _criar_planejamento(
        client, [ordens_ids[1]], nome="Planejamento B"
    )
    assert primeiro.status_code == 201, primeiro.text
    assert segundo.status_code == 201, segundo.text

    planejamento_id = segundo.json()["id_planejamento"]

    resposta = client.put(
        f"/api/planejamentos/{planejamento_id}",
        json={
            "nome": "Planejamento B",
            "ordens_ids": [ordens_ids[1], ordens_ids[0]],
        },
    )

    assert resposta.status_code == 409

def test_atualizacao_de_planejamento_inexistente(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200

    resposta = client.put(
        f"/api/planejamentos/{uuid4()}",
        json={
            "nome": "Planejamento inexistente",
            "ordens_ids": [str(uuid4())],
        },
    )

    assert resposta.status_code == 404

def test_operador_nao_pode_atualizar_planejamento(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    assert _login(
        client, state.operator_email, state.password
    ).status_code == 200

    resposta = client.put(
        f"/api/planejamentos/{uuid4()}",
        json={
            "nome": "Planejamento não autorizado",
            "ordens_ids": [str(uuid4())],
        },
    )

    assert resposta.status_code == 403
