from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import text


def _login(client, email, password):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _session_count(engine):
    with engine.connect() as connection:
        return connection.scalar(text("SELECT count(*) FROM sessoes"))


def test_login_com_credenciais_validas_cria_sessao_e_retorna_perfil(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    response = _login(client, state.email, state.password)

    assert response.status_code == 200
    body = response.json()
    assert body["usuario"]["id"] == str(state.user_id)
    assert body["usuario"]["nome"] == "Usuário de Teste"
    assert body["usuario"]["email"] == state.email
    assert body["usuario"]["perfis"] == ["PLANEJADOR"]
    assert "senha" not in body["usuario"]
    assert "senha_hash" not in response.text
    assert state.password not in response.text

    session_cookie = response.cookies.get("setupflow_session")
    assert session_cookie
    cookie_header = response.headers["set-cookie"].lower()
    assert "httponly" in cookie_header
    assert "samesite=lax" in cookie_header
    assert session_cookie not in response.text
    assert _session_count(state.engine) == 1


def test_senha_incorreta_e_rejeitada_sem_criar_sessao(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    response = _login(client, state.email, "SenhaErrada!2026")

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível entrar. Verifique suas credenciais."
    assert "set-cookie" not in response.headers
    assert _session_count(state.engine) == 0


def test_email_nao_cadastrado_retorna_mensagem_generica(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    response = _login(client, "nao.existe@example.com", state.password)

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível entrar. Verifique suas credenciais."
    assert "set-cookie" not in response.headers
    assert _session_count(state.engine) == 0


def test_payload_invalido_nao_repete_a_senha_na_resposta(seeded_auth):
    response = seeded_auth.client.post(
        "/api/auth/login",
        json={"email": "email-invalido", "password": "NAO_REPETIR_ESTE_SEGREDO"},
    )

    assert response.status_code == 422
    assert "NAO_REPETIR_ESTE_SEGREDO" not in response.text
    assert "set-cookie" not in response.headers
    assert _session_count(seeded_auth.state.engine) == 0


def test_me_sem_cookie_retorna_401(seeded_auth):
    response = seeded_auth.client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_com_sessao_valida_retorna_identidade_e_perfis(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    body = response.json()["usuario"]
    assert body["id"] == str(state.user_id)
    assert body["nome"] == "Usuário de Teste"
    assert body["email"] == state.email
    assert body["perfis"] == ["PLANEJADOR"]
    assert "senha" not in body
    assert "senha_hash" not in response.text
    assert state.password not in response.text


def test_me_retorna_perfil_de_operador(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    login = _login(client, state.operator_email, state.password)
    assert login.status_code == 200

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    body = response.json()["usuario"]
    assert body["id"] == str(state.operator_user_id)
    assert body["perfis"] == ["OPERADOR"]


def test_me_rejeita_sessao_expirada(seeded_auth, monkeypatch):
    client, state = seeded_auth.client, seeded_auth.state
    login = _login(client, state.email, state.password)
    assert login.status_code == 200

    class ExpiredSessionClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(days=1)

    from app.api.routes import auth

    monkeypatch.setattr(auth, "datetime", ExpiredSessionClock)

    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_logout_invalida_a_sessao(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    login = _login(client, state.email, state.password)
    assert login.status_code == 200
    token = login.cookies.get("setupflow_session")
    assert token
    token_hash = sha256(token.encode("utf-8")).hexdigest()

    logout = client.post("/api/auth/logout")

    assert logout.status_code == 204
    assert "setupflow_session" not in client.cookies
    with state.engine.connect() as connection:
        invalidated_at = connection.scalar(
            text("SELECT invalidada_em FROM sessoes WHERE token_hash = :token_hash"),
            {"token_hash": token_hash},
        )
    assert invalidated_at is not None
    assert client.get("/api/auth/me").status_code == 401
