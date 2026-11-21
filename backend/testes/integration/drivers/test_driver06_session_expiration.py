from datetime import datetime, timedelta
from time import perf_counter

def test_driver06_sessao_invalidada_rejeita_20_tentativas(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = client.post(
        "/api/auth/login",
        json={"email": state.email, "password": state.password},
    )

    assert login.status_code == 200

    token = login.cookies.get("setupflow_session")
    assert token is not None

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204

    # Reutiliza o token que foi invalidado pelo logout.
    client.cookies.set("setupflow_session", token)

    tempos_resposta = []

    for _ in range(20):
        inicio = perf_counter()

        response = client.get("/api/families")

        duracao = perf_counter() - inicio
        tempos_resposta.append(duracao)

        assert response.status_code == 401
        assert duracao <= 2.0

    print(
        f"Driver06: 20 acessos rejeitados. "
        f"Maior tempo: {max(tempos_resposta):.4f}s"
    )

def test_driver06_rota_protegida_com_sessao_valida_e_invalidada(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = client.post(
        "/api/auth/login",
        json={"email": state.email, "password": state.password},
    )
    assert login.status_code == 200

    token = login.cookies.get("setupflow_session")
    assert token is not None

    # A sessão válida permite o acesso.
    response = client.get("/api/families")
    assert response.status_code == 200

    # O logout invalida a sessão.
    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204

    # A sessão invalidada não pode acessar a mesma rota.
    client.cookies.set("setupflow_session", token)

    response = client.get("/api/families")
    assert response.status_code == 401

def test_driver06_rota_protegida_rejeita_sessao_expirada(
    seeded_auth, monkeypatch
):
    client, state = seeded_auth.client, seeded_auth.state

    login = client.post(
        "/api/auth/login",
        json={"email": state.email, "password": state.password},
    )
    assert login.status_code == 200

    class ExpiredSessionClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(days=1)

    from app.api import deps

    monkeypatch.setattr(deps, "datetime", ExpiredSessionClock)

    response = client.get("/api/families")
    assert response.status_code == 401


def test_driver06_sessao_valida_sem_permissao_retorna_403(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    login = client.post(
        "/api/auth/login",
        json={
            "email": state.operator_email,
            "password": state.password,
        },
    )
    assert login.status_code == 200

    response = client.get("/api/families")
    assert response.status_code == 403
