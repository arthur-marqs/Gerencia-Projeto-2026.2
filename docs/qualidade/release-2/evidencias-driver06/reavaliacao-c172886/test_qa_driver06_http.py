"""Testes adicionais de QA, criados nesta revisão; Uvicorn + PostgreSQL reais.

Executar a partir de backend, com TEST_DATABASE_URL isolada e PYTHONPATH=.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from hashlib import sha256
from http.cookies import SimpleCookie
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import pytest
from sqlalchemy import text

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'backend/app').is_dir())
sys.path.insert(0, str(ROOT / 'backend/testes/integration'))
from conftest import auth_test_context, auth_state  # noqa: E402,F401

OUTPUT = Path(__file__).parent
BASE = 'http://127.0.0.1:8006'
ROTAS = ['/api/families', '/api/maquinas', '/api/produtos',
         '/api/ordens-producao', '/api/planejamentos', '/api/tempos-setup',
         '/api/usuarios', '/api/auth/me']

def request(path, token=None, data=None):
    headers = {'Origin': 'http://localhost:5173'}
    if token:
        headers['Cookie'] = 'setupflow_session=' + token
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = Request(BASE + path, headers=headers,
                  data=json.dumps(data).encode() if data is not None else None)
    try:
        response = urlopen(req, timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read(), response.headers

@pytest.fixture(scope='session')
def real_api(auth_test_context):
    with (OUTPUT / 'uvicorn-http.txt').open('w', encoding='utf-8') as log:
        proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app',
                                 '--host', '127.0.0.1', '--port', '8006'],
                                cwd=ROOT / 'backend', env=os.environ.copy(),
                                stdout=log, stderr=log,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(50):
                try:
                    if request('/api/health')[0] == 200:
                        break
                except URLError:
                    time.sleep(0.1)
            else:
                pytest.fail('API de QA não iniciou')
            yield
        finally:
            proc.terminate()
            proc.wait(timeout=10)

@pytest.mark.parametrize('estado', ['invalidada', 'expirada', 'desconhecida'])
def test_qa_http_20_tentativas_por_estado(real_api, auth_state, estado):
    with auth_state.engine.begin() as db:
        db.execute(text("""INSERT INTO usuario_perfil (id_usuario,id_perfil)
            SELECT :id,id_perfil FROM perfis WHERE codigo='ADMINISTRADOR'"""),
                   {'id': auth_state.user_id})
    status, _, headers = request('/api/auth/login', data={
        'email': auth_state.email, 'password': auth_state.password})
    assert status == 200
    cookie = SimpleCookie()
    cookie.load(headers['Set-Cookie'])
    token = cookie['setupflow_session'].value
    for rota in ROTAS:
        assert request(rota, token)[0] == 200, rota
    token_hash = sha256(token.encode()).hexdigest()
    if estado == 'invalidada':
        assert request('/api/auth/logout', token, {})[0] == 204
        with auth_state.engine.connect() as db:
            assert db.scalar(text('SELECT invalidada_em FROM sessoes WHERE token_hash=:hash'),
                             {'hash':token_hash}) is not None
    elif estado == 'expirada':
        with auth_state.engine.begin() as db:
            db.execute(text("""UPDATE sessoes SET criada_em=now()-interval '2 days',
                expira_em=now()-interval '1 day' WHERE token_hash=:hash"""), {'hash':token_hash})
    else:
        token = 'token-inexistente-exclusivo-qa-driver06'
    amostras = []
    for i in range(20):
        rota = ROTAS[i % len(ROTAS)]
        inicio = time.perf_counter()
        status, body, _ = request(rota, token)
        duracao = time.perf_counter() - inicio
        amostras.append({'tentativa':i+1,'rota':rota,'status':status,'segundos':duracao})
        assert status == 401
        assert json.loads(body)['detail'] == 'Sessão inválida ou expirada.'
        assert duracao <= 2
    # Operação de escrita recusada, sem persistência.
    assert request('/api/families', token, {'code':'QA-D06','name':'Não persistir'})[0] == 401
    with auth_state.engine.connect() as db:
        assert db.scalar(text("SELECT count(*) FROM families WHERE code='QA-D06'")) == 0
    result = {'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'estado':estado,'tipo':'HTTP real + Uvicorn + PostgreSQL',
              'amostras':amostras,'maximo_segundos':max(a['segundos'] for a in amostras)}
    (OUTPUT / ('http-' + estado + '.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f"{estado}: 20/20 recusadas, máximo {result['maximo_segundos']:.6f}s")
