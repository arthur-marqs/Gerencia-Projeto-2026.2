from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client):
    return client.post(
        "/api/produtos",
        json={"codigo": "PRD-DR02", "nome": "Produto Driver02", "unidade": "un"},
    ).json()


def _cadastrar(client, dados, chave):
    return client.post(
        "/api/ordens-producao",
        json=dados,
        headers={"Idempotency-Key": str(chave)},
    )


def test_driver02_20_operacoes_com_cinco_reenvios(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)

    chaves = []
    for indice in range(20):
        chave = uuid4()
        chaves.append(chave)
        dados = {
            "codigo": f"DR02-{indice:02d}",
            "produto_id": produto["id_produto"],
            "quantidade": "12.500",
        }

        original = _cadastrar(client, dados, chave)
        assert original.status_code == 201
        id_ordem = original.json()["id_ordem"]

        for _ in range(5):
            repetida = _cadastrar(client, dados, chave)
            assert repetida.status_code == 200
            assert repetida.json()["id_ordem"] == id_ordem

    with state.engine.connect() as connection:
        contagens = dict(
            connection.execute(
                text(
                    """
                    SELECT operacao.chave, count(ordem.id_ordem)
                    FROM ordens_producao_operacoes AS operacao
                    LEFT JOIN ordens_producao AS ordem
                        ON ordem.operacao_id = operacao.id_operacao
                    WHERE operacao.usuario_id = :usuario_id
                    GROUP BY operacao.chave
                    """
                ),
                {"usuario_id": state.user_id},
            ).all()
        )

    assert set(contagens) == set(chaves)
    assert all(total == 1 for total in contagens.values())


def test_nova_chave_com_novo_codigo_cria_ordem_distinta(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    dados = {
        "produto_id": produto["id_produto"],
        "quantidade": "7.250",
    }

    primeira = _cadastrar(
        client,
        {"codigo": "DR02-NOVA-01", **dados},
        uuid4(),
    )
    segunda = _cadastrar(
        client,
        {"codigo": "DR02-NOVA-02", **dados},
        uuid4(),
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 201
    assert primeira.json()["id_ordem"] != segunda.json()["id_ordem"]

    with state.engine.connect() as connection:
        total = connection.scalar(
            text(
                """
                SELECT count(*)
                FROM ordens_producao
                WHERE produto_id = :produto_id AND quantidade = 7.250
                """
            ),
            {"produto_id": produto["id_produto"]},
        )
    assert total == 2


def test_mesma_chave_com_conteudo_diferente_retorna_conflito(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    dados = {
        "codigo": "DR02-CONFLITO",
        "produto_id": produto["id_produto"],
        "quantidade": "2",
    }

    original = _cadastrar(client, dados, chave)
    alterada = _cadastrar(client, {**dados, "quantidade": "3"}, chave)

    assert original.status_code == 201
    assert alterada.status_code == 409
    assert alterada.json()["detail"] == (
        "A chave de idempotência já foi utilizada com outro conteúdo."
    )
    with state.engine.connect() as connection:
        salvo = connection.execute(
            text(
                """
                SELECT count(*) AS total, min(codigo) AS codigo,
                    min(quantidade) AS quantidade
                FROM ordens_producao
                """
            )
        ).mappings().one()
    assert salvo["total"] == 1
    assert salvo["codigo"] == "DR02-CONFLITO"
    assert str(salvo["quantidade"]) == "2.000"


def test_reenvio_imediatamente_antes_e_depois_de_24_horas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    dados = {
        "codigo": "DR02-24H",
        "produto_id": produto["id_produto"],
        "quantidade": "1",
    }

    original = _cadastrar(client, dados, chave)
    assert original.status_code == 201

    antes_de_24h = _cadastrar(client, dados, chave)
    assert antes_de_24h.status_code == 200
    assert antes_de_24h.json()["id_ordem"] == original.json()["id_ordem"]

    with state.engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE ordens_producao_operacoes
                SET criado_em = CURRENT_TIMESTAMP - INTERVAL '24 hours'
                WHERE chave = :chave AND usuario_id = :usuario_id
                """
            ),
            {"chave": chave, "usuario_id": state.user_id},
        )

    ao_completar_24h = _cadastrar(client, dados, chave)
    assert ao_completar_24h.status_code == 200
    assert ao_completar_24h.json()["id_ordem"] == original.json()["id_ordem"]


def test_reenvios_simultaneos_criam_uma_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    dados = {
        "codigo": "DR02-SIMULTANEA",
        "produto_id": produto["id_produto"],
        "quantidade": "4",
    }
    token = client.cookies.get("setupflow_session")

    def enviar():
        with TestClient(state.app) as concorrente:
            concorrente.cookies.set("setupflow_session", token)
            return _cadastrar(concorrente, dados, chave)

    with ThreadPoolExecutor(max_workers=5) as executor:
        respostas = list(executor.map(lambda _: enviar(), range(5)))

    assert all(resposta.status_code in (200, 201) for resposta in respostas)
    assert len({resposta.json()["id_ordem"] for resposta in respostas}) == 1
    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE codigo = 'DR02-SIMULTANEA'")
        )
    assert total == 1


def test_falha_antes_da_confirmacao_nao_deixa_ordem_parcial(
    seeded_auth,
    monkeypatch,
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    dados = {
        "codigo": "DR02-ROLLBACK",
        "produto_id": produto["id_produto"],
        "quantidade": "5",
    }
    commit_original = Session.commit
    falhar_commit = True

    def commit_com_falha_inicial(session):
        nonlocal falhar_commit
        if falhar_commit:
            falhar_commit = False
            raise IntegrityError("falha simulada antes do commit", {}, RuntimeError())
        commit_original(session)

    monkeypatch.setattr(Session, "commit", commit_com_falha_inicial)
    falha = _cadastrar(client, dados, chave)
    assert falha.status_code == 409

    with state.engine.connect() as connection:
        ordens_parciais = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE codigo = 'DR02-ROLLBACK'")
        )
        operacoes_parciais = connection.scalar(
            text(
                """
                SELECT count(*)
                FROM ordens_producao_operacoes
                WHERE chave = :chave
                """
            ),
            {"chave": chave},
        )
    assert ordens_parciais == 0
    assert operacoes_parciais == 0

    sucesso = _cadastrar(client, dados, chave)
    assert sucesso.status_code == 201

    with state.engine.connect() as connection:
        total = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE codigo = 'DR02-ROLLBACK'")
        )
    assert total == 1


def test_chave_ausente_ou_invalida_nao_persiste_ordem(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    dados = {
        "codigo": "DR02-CHAVE-INVALIDA",
        "produto_id": produto["id_produto"],
        "quantidade": "1",
    }

    ausente = client.post("/api/ordens-producao", json=dados)
    invalida = client.post(
        "/api/ordens-producao",
        json=dados,
        headers={"Idempotency-Key": "nao-e-uuid"},
    )

    assert ausente.status_code == 422
    assert invalida.status_code == 422
    with state.engine.connect() as connection:
        total = connection.scalar(
            text(
                "SELECT count(*) FROM ordens_producao "
                "WHERE codigo = 'DR02-CHAVE-INVALIDA'"
            )
        )
    assert total == 0
