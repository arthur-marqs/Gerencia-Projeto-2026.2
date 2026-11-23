"""Casos adicionais de QA: fronteira de expiração, relógio controlado e banco real."""
from pathlib import Path
import sys
from datetime import timedelta
import pytest
from sqlalchemy import text

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'backend/app').is_dir())
sys.path.insert(0, str(ROOT / 'backend/testes/integration'))
from conftest import auth_test_context, auth_state, client, seeded_auth  # noqa: E402,F401

@pytest.mark.parametrize('micros,status', [(-1, 200), (0, 401), (1, 401)])
def test_qa_fronteira_expiracao(seeded_auth, monkeypatch, micros, status):
    state = seeded_auth.state
    client = seeded_auth.client
    assert client.post('/api/auth/login', json={
        'email': state.email, 'password': state.password}).status_code == 200
    with state.engine.connect() as db:
        expira = db.scalar(text('SELECT expira_em FROM sessoes WHERE id_usuario=:id'), {'id':state.user_id})
    class Clock:
        @classmethod
        def now(cls, tz=None):
            return expira + timedelta(microseconds=micros)
    from app.api import deps
    monkeypatch.setattr(deps, 'datetime', Clock)
    assert client.get('/api/families').status_code == status
