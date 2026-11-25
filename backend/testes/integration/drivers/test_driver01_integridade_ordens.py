"""Testes do Driver01: rollback em falhas durante a persistência de ordens."""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_produto(client):
    resposta = client.post(
        "/api/produtos",
        json={"codigo": "PRD-DR01", "nome": "Produto Driver01", "unidade": "un"},
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _criar_ordem(client, codigo: str):
    produto = _criar_produto(client)
    resposta = client.post(
        "/api/ordens-producao",
        json={
            "codigo": codigo,
            "produto_id": produto["id_produto"],
            "quantidade": 5,
        },
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _cadastrar(client, dados, chave):
    return client.post(
        "/api/ordens-producao",
        json=dados,
        headers={"Idempotency-Key": str(chave)},
    )


def _injetar_falha_apos_sql(monkeypatch, ponto: str):
    """Executa o flush real e interrompe antes do commit da transação."""
    falha = OperationalError(
        ponto.upper(),
        {},
        ConnectionError("falha temporária simulada no banco"),
    )

    if ponto == "flush":
        flush_original = Session.flush
        ja_falhou = False

        def flush_com_falha(session, *args, **kwargs):
            nonlocal ja_falhou

            # Ignora flushes vazios, como os acionados por consultas.
            havia_alteracoes = bool(
                session.new or session.dirty or session.deleted
            )

            resultado = flush_original(session, *args, **kwargs)

            # Interrompe somente depois de executar SQL de escrita.
            if havia_alteracoes and not ja_falhou:
                ja_falhou = True
                raise falha

            return resultado

        monkeypatch.setattr(Session, "flush", flush_com_falha)

        def restaurar():
            monkeypatch.setattr(Session, "flush", flush_original)

        return restaurar

    commit_original = Session.commit
    flush_original = Session.flush

    def commit_com_falha(session):
        # Executa o SQL da alteração, mas não confirma a transação.
        flush_original(session)
        raise falha

    monkeypatch.setattr(Session, "commit", commit_com_falha)

    def restaurar():
        monkeypatch.setattr(Session, "commit", commit_original)

    return restaurar

def _dados_prazo(prazo: date, prioridade: str):
    return {"prazo": prazo.isoformat(), "prioridade": prioridade}


@pytest.mark.parametrize("indice", range(5))
def test_driver01_falha_apos_flush_no_cadastro_nao_deixa_registros_parciais(
    seeded_auth, monkeypatch, indice
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    codigo = f"DR01-FLUSH-{indice}"
    dados = {
        "codigo": codigo,
        "produto_id": produto["id_produto"],
        "quantidade": 5,
    }

    restaurar = _injetar_falha_apos_sql(monkeypatch, "flush")
    falha = _cadastrar(client, dados, chave)
    restaurar()

    assert falha.status_code == 503
    assert "Não foi possível confirmar a gravação" in falha.json()["detail"]
    with state.engine.connect() as connection:
        total_ordens = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE codigo = :codigo"),
            {"codigo": codigo},
        )
        total_operacoes = connection.scalar(
            text("SELECT count(*) FROM ordens_producao_operacoes WHERE chave = :chave"),
            {"chave": chave},
        )
    assert total_ordens == 0
    assert total_operacoes == 0

    repeticao = _cadastrar(client, dados, chave)
    assert repeticao.status_code == 201, repeticao.text


@pytest.mark.parametrize("indice", range(5))
def test_driver01_falha_apos_flush_no_commit_nao_deixa_ordem_parcial(
    seeded_auth, monkeypatch, indice
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    produto = _criar_produto(client)
    chave = uuid4()
    codigo = f"DR01-COMMIT-{indice}"
    dados = {
        "codigo": codigo,
        "produto_id": produto["id_produto"],
        "quantidade": 7,
    }

    restaurar = _injetar_falha_apos_sql(monkeypatch, "commit")
    falha = _cadastrar(client, dados, chave)
    restaurar()

    assert falha.status_code == 503
    with state.engine.connect() as connection:
        total_ordens = connection.scalar(
            text("SELECT count(*) FROM ordens_producao WHERE codigo = :codigo"),
            {"codigo": codigo},
        )
        total_operacoes = connection.scalar(
            text("SELECT count(*) FROM ordens_producao_operacoes WHERE chave = :chave"),
            {"chave": chave},
        )
    assert total_ordens == 0
    assert total_operacoes == 0

    repeticao = _cadastrar(client, dados, chave)
    assert repeticao.status_code == 201, repeticao.text


@pytest.mark.parametrize("indice", range(5))
def test_driver01_falha_ao_atualizar_duracao_preserva_valor_anterior(
    seeded_auth, monkeypatch, indice
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, f"DR01-DUR-{indice}")
    url = f"/api/ordens-producao/{ordem['id_ordem']}/duracao-estimada"
    inicial = client.patch(url, json={"duracao_estimada_minutos": 30})
    assert inicial.status_code == 200, inicial.text

    restaurar = _injetar_falha_apos_sql(monkeypatch, "commit")
    falha = client.patch(url, json={"duracao_estimada_minutos": 90})
    restaurar()

    assert falha.status_code == 503
    with state.engine.connect() as connection:
        duracao_salva = connection.scalar(
            text(
                "SELECT duracao_estimada_minutos FROM ordens_producao "
                "WHERE id_ordem = :id_ordem"
            ),
            {"id_ordem": ordem["id_ordem"]},
        )
    assert duracao_salva == 30

    repeticao = client.patch(url, json={"duracao_estimada_minutos": 90})
    assert repeticao.status_code == 200, repeticao.text
    assert repeticao.json()["duracao_estimada_minutos"] == 90


@pytest.mark.parametrize("indice", range(5))
def test_driver01_falha_ao_atualizar_prazo_preserva_dados_anteriores(
    seeded_auth, monkeypatch, indice
):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    ordem = _criar_ordem(client, f"DR01-PRAZO-{indice}")
    url = f"/api/ordens-producao/{ordem['id_ordem']}"
    prazo_inicial = date.today() + timedelta(days=7)
    prazo_novo = date.today() + timedelta(days=14)

    inicial = client.put(
        url,
        json=_dados_prazo(prazo_inicial, "Média"),
    )
    assert inicial.status_code == 200, inicial.text

    restaurar = _injetar_falha_apos_sql(monkeypatch, "commit")
    falha = client.put(
        url,
        json=_dados_prazo(prazo_novo, "Alta"),
    )
    restaurar()

    assert falha.status_code == 503
    with state.engine.connect() as connection:
        salvo = connection.execute(
            text("SELECT prazo, prioridade FROM ordens_producao WHERE id_ordem = :id_ordem"),
            {"id_ordem": ordem["id_ordem"]},
        ).mappings().one()
    assert salvo["prazo"] == prazo_inicial
    assert salvo["prioridade"] == "Média"

    repeticao = client.put(
        url,
        json=_dados_prazo(prazo_novo, "Alta"),
    )
    assert repeticao.status_code == 200, repeticao.text
    assert repeticao.json()["prazo"] == prazo_novo.isoformat()
    assert repeticao.json()["prioridade"] == "Alta"
