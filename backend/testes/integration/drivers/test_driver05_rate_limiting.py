from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


IP_ORIGEM = "192.0.2.10"
SENHA_VALIDA = "SenhaDriver05!2026"
SENHA_INCORRETA = "SenhaIncorreta!2026"


class ControlledClock(datetime):
    current = datetime.now(timezone.utc)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.current.replace(tzinfo=None)
        return cls.current.astimezone(tz)

    @classmethod
    def advance(cls, duration):
        cls.current += duration


def _login(client, email, password):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _session_count(engine):
    with engine.connect() as connection:
        return connection.scalar(text("SELECT count(*) FROM sessoes"))


def _create_valid_user(engine, email):
    from app.core.security import hash_password

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO usuarios (nome, email, senha_hash, ativo)
                VALUES (:nome, :email, :senha_hash, TRUE)
                """
            ),
            {
                "nome": "Usuário Driver05",
                "email": email,
                "senha_hash": hash_password(SENHA_VALIDA),
            },
        )


def _second_api_instance(engine):
    from app.api.deps import get_db
    from app.api.routes import auth

    app = FastAPI()
    app.include_router(auth.router, prefix="/api/auth")
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture(autouse=True)
def controlled_clock(monkeypatch, auth_test_context):
    from app.api.routes import auth

    ControlledClock.current = datetime.now(timezone.utc)
    monkeypatch.setattr(auth, "datetime", ControlledClock)


@pytest.mark.parametrize(
    "cycle",
    range(1, 21),
    ids=lambda cycle: f"cycle-{cycle:02}",
)
def test_driver05_rejeita_200_tentativas_bloqueadas_e_isola_20_contas(
    cycle,
    seeded_auth,
):
    state, client = seeded_auth.state, seeded_auth.client
    victim_email = f"driver05.victim.{cycle:02}@example.com"
    alternate_email = f"driver05.alternate.{cycle:02}@example.com"

    with state.engine.begin() as connection:
        connection.execute(
            text("UPDATE usuarios SET email = :email WHERE id_usuario = :user_id"),
            {"email": victim_email, "user_id": state.user_id},
        )

    state.email = victim_email
    second_app = _second_api_instance(state.engine)
    second_client = TestClient(
        second_app,
        client=(IP_ORIGEM, 50001),
    )

    try:
        clients = (client, second_client)
        failures = [
            _login(clients[index % 2], victim_email, SENHA_INCORRETA)
            for index in range(5)
        ]

        assert [response.status_code for response in failures] == [
            401,
            401,
            401,
            401,
            429,
        ]
        assert failures[-1].json()["detail"] == (
            "Muitas tentativas. Tente novamente em 15 minutos."
        )
        assert all("set-cookie" not in response.headers for response in failures)
        assert _session_count(state.engine) == 0

        ControlledClock.advance(timedelta(minutes=14))
        for index in range(10):
            response = _login(
                clients[index % 2],
                victim_email,
                state.password if index == 4 else SENHA_INCORRETA,
            )
            assert response.status_code == 429
            assert response.json()["detail"] == (
                "Muitas tentativas. Tente novamente em 15 minutos."
            )
            assert "set-cookie" not in response.headers
            assert _session_count(state.engine) == 0

        _create_valid_user(state.engine, alternate_email)
        alternate_login = _login(client, alternate_email, SENHA_VALIDA)

        assert alternate_login.status_code == 200
        assert alternate_login.json()["usuario"]["email"] == alternate_email
        assert _session_count(state.engine) == 1
    finally:
        second_client.close()
        second_app.dependency_overrides.clear()


def test_driver05_permite_login_ao_completar_15_minutos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    for _ in range(4):
        assert _login(client, state.email, SENHA_INCORRETA).status_code == 401

    fifth_failure = _login(client, state.email, SENHA_INCORRETA)
    assert fifth_failure.status_code == 429

    ControlledClock.advance(timedelta(minutes=15) - timedelta(microseconds=1))
    still_blocked = _login(client, state.email, state.password)
    assert still_blocked.status_code == 429
    assert "set-cookie" not in still_blocked.headers
    assert _session_count(state.engine) == 0

    ControlledClock.advance(timedelta(microseconds=1))
    allowed = _login(client, state.email, state.password)

    assert allowed.status_code == 200
    assert allowed.cookies.get("setupflow_session")
    assert _session_count(state.engine) == 1


def test_driver05_conta_falhas_em_janela_movel_de_5_minutos(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state

    for _ in range(4):
        assert _login(client, state.email, SENHA_INCORRETA).status_code == 401

    with state.engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE falhas_login
                SET ocorrida_em = CURRENT_TIMESTAMP - INTERVAL '6 minutes'
                WHERE email_tentado = :email AND ip_origem = :ip
                """
            ),
            {"email": state.email, "ip": IP_ORIGEM},
        )

    first_failure_after_window = _login(client, state.email, SENHA_INCORRETA)
    assert first_failure_after_window.status_code == 401

    for _ in range(3):
        response = _login(client, state.email, SENHA_INCORRETA)
        assert response.status_code == 401

    fifth_failure_in_window = _login(client, state.email, SENHA_INCORRETA)
    assert fifth_failure_in_window.status_code == 429
