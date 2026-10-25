"""Fixtures de integração da US01. Usam exclusivamente um banco *_test."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def auth_test_context():
    test_database_url = os.getenv("TEST_DATABASE_URL")
    if not test_database_url:
        pytest.fail("Defina TEST_DATABASE_URL para um banco PostgreSQL de teste terminado em _test.")

    try:
        parsed_url = make_url(test_database_url)
    except ArgumentError:
        pytest.fail("TEST_DATABASE_URL deve ser uma URL SQLAlchemy válida.")

    if parsed_url.get_backend_name() != "postgresql":
        pytest.fail("TEST_DATABASE_URL deve apontar para um banco PostgreSQL.")

    if (
        not parsed_url.database
        or not parsed_url.database.endswith("_test")
        or parsed_url.database == "setupflow_dev"
    ):
        pytest.fail("Testes recusados: o nome do banco deve terminar em _test.")

    if not parsed_url.username:
        pytest.fail("TEST_DATABASE_URL deve informar o usuário PostgreSQL.")

    test_url = parsed_url.set(drivername="postgresql+psycopg")
    for name, value in {
        "DB_USER": parsed_url.username or "",
        "DB_PASSWORD": parsed_url.password or "",
        "DB_HOST": parsed_url.host or "localhost",
        "DB_PORT": str(parsed_url.port or 5432),
        "DB_NAME": parsed_url.database,
    }.items():
        os.environ[name] = value

    backend_dir = Path(__file__).resolve().parents[2]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "migrations"))
    config.set_main_option(
        "sqlalchemy.url",
        test_url.render_as_string(hide_password=False).replace("%", "%%"),
    )

    engine = create_engine(test_url)
    app = None
    try:
        command.upgrade(config, "head")

        from app.api.deps import get_db
        from app.main import app as application

        app = application
        factory = sessionmaker(bind=engine, expire_on_commit=False)

        def override_get_db():
            with factory() as db:
                yield db

        app.dependency_overrides[get_db] = override_get_db
        yield SimpleNamespace(app=app, engine=engine, factory=factory)
    finally:
        if app is not None:
            app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def auth_state(auth_test_context):
    """Limpa e prepara os dados de cada teste no banco isolado *_test."""
    with auth_test_context.engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE falhas_login, sessoes, usuario_perfil,
                    usuarios, controle_tentativas_login CASCADE
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO perfis (codigo, nome, descricao)
                VALUES
                    ('PLANEJADOR', 'Planejador de Produção', 'Perfil de teste'),
                    ('OPERADOR', 'Operador', 'Perfil de teste')
                ON CONFLICT (codigo) DO NOTHING
                """
            )
        )
        user_id = connection.execute(
            text(
                """
                INSERT INTO usuarios (nome, email, senha_hash, ativo)
                VALUES (:nome, :email, :senha_hash, TRUE)
                RETURNING id_usuario
                """
            ),
            {
                "nome": "Usuário de Teste",
                "email": "us01.teste@example.com",
                "senha_hash": _hash_password("SenhaTesteUS01!2026"),
            },
        ).scalar_one()
        connection.execute(
            text(
                """
                INSERT INTO usuario_perfil (id_usuario, id_perfil)
                SELECT :user_id, id_perfil FROM perfis WHERE codigo = 'PLANEJADOR'
                """
            ),
            {"user_id": user_id},
        )
        operator_user_id = connection.execute(
            text(
                """
                INSERT INTO usuarios (nome, email, senha_hash, ativo)
                VALUES (:nome, :email, :senha_hash, TRUE)
                RETURNING id_usuario
                """
            ),
            {
                "nome": "Operador de Teste",
                "email": "us01.operador@example.com",
                "senha_hash": _hash_password("SenhaTesteUS01!2026"),
            },
        ).scalar_one()
        connection.execute(
            text(
                """
                INSERT INTO usuario_perfil (id_usuario, id_perfil)
                SELECT :user_id, id_perfil FROM perfis WHERE codigo = 'OPERADOR'
                """
            ),
            {"user_id": operator_user_id},
        )

    return SimpleNamespace(
        app=auth_test_context.app,
        engine=auth_test_context.engine,
        user_id=user_id,
        email="us01.teste@example.com",
        password="SenhaTesteUS01!2026",
        operator_user_id=operator_user_id,
        operator_email="us01.operador@example.com",
    )


def _hash_password(password: str) -> str:
    # Import tardio: garante que a configuração de teste já foi selecionada.
    from app.core.security import hash_password

    return hash_password(password)


@pytest.fixture
def client(auth_state):
    from fastapi.testclient import TestClient

    with TestClient(
        auth_state.app,
        client=("192.0.2.10", 50000),
        headers={"Origin": "http://localhost:5173"},
    ) as test_client:
        yield test_client


@pytest.fixture
def seeded_auth(auth_state, client):
    return SimpleNamespace(state=auth_state, client=client)
