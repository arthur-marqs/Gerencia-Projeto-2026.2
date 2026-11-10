"""US-32: exercita a API com PostgreSQL real, inclusive disputas entre transações."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


API = "/api/usuarios"
SENHA = "SenhaUS32!2026"


def payload(**alteracoes):
    return {"nome": "Ana", "email": "ana@empresa.com", "senha": SENHA,
            "perfis": ["PLANEJADOR"], **alteracoes}


def login(client, email, senha=SENHA):
    return client.post("/api/auth/login", json={"email": email, "password": senha})


@pytest.fixture
def admin(auth_state, client):
    with auth_state.engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO usuario_perfil (id_usuario, id_perfil)
            SELECT :id, id_perfil FROM perfis WHERE codigo = 'ADMINISTRADOR'
        """), {"id": auth_state.user_id})
    assert login(client, auth_state.email, auth_state.password).status_code == 200
    return client


def criar(admin, **alteracoes):
    response = admin.post(API, json=payload(**alteracoes))
    assert response.status_code == 201, response.text
    return response.json()


def test_cadastro_consulta_multiplos_perfis_e_login(admin, auth_state):
    novo = criar(admin, nome="  Ana  ", email="  ANA@EMPRESA.COM  ",
                 perfis=["PLANEJADOR", "OPERADOR", "OPERADOR"])
    assert novo == {"id": novo["id"], "nome": "Ana", "email": "ana@empresa.com",
                    "perfis": ["OPERADOR", "PLANEJADOR"], "ativo": True}
    assert admin.get(f"{API}/{novo['id']}").json() == novo
    assert novo in admin.get(API).json()
    with auth_state.engine.connect() as conn:
        senha_hash = conn.scalar(text("SELECT senha_hash FROM usuarios WHERE id_usuario = :id"), {"id": novo["id"]})
    assert senha_hash != SENHA
    assert senha_hash not in admin.get(API).text
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as pessoa:
        assert login(pessoa, " ANA@EMPRESA.COM ").status_code == 200
        assert pessoa.get("/api/produtos").status_code == 200
        assert pessoa.get(API).status_code == 403


def test_edicao_sem_senha_aplica_permissoes_na_sessao_aberta(admin, auth_state):
    novo = criar(admin)
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as pessoa:
        assert login(pessoa, novo["email"]).status_code == 200
        assert pessoa.get("/api/produtos").status_code == 200
        response = admin.put(f"{API}/{novo['id']}", json=payload(
            nome="Ana editada", email=" NOVO@EMPRESA.COM ", senha="", perfis=["OPERADOR"]))
        assert response.status_code == 200
        assert response.json()["email"] == "novo@empresa.com"
        assert pessoa.get("/api/auth/me").json()["usuario"]["perfis"] == ["OPERADOR"]
        assert pessoa.get("/api/produtos").status_code == 403
        assert login(pessoa, "novo@empresa.com").status_code == 200


@pytest.mark.parametrize("senha", ["", None])
def test_senha_opcional_preserva_hash(admin, auth_state, senha):
    novo = criar(admin)
    with auth_state.engine.connect() as conn:
        anterior = conn.scalar(text("SELECT senha_hash FROM usuarios WHERE id_usuario = :id"), {"id": novo["id"]})
    assert admin.put(f"{API}/{novo['id']}", json=payload(senha=senha)).status_code == 200
    with auth_state.engine.connect() as conn:
        assert conn.scalar(text("SELECT senha_hash FROM usuarios WHERE id_usuario = :id"), {"id": novo["id"]}) == anterior


@pytest.mark.parametrize("dados,campo", [
    ({"nome": "  "}, "nome"), ({"nome": "A" * 151}, "nome"),
    ({"email": "invalido"}, "email"), ({"email": "a" * 250 + "@a.com"}, "email"),
    ({"perfis": []}, "perfis"), ({"perfis": ["INEXISTENTE"]}, "perfis"),
    ({"senha": "curta"}, "senha"),
])
def test_validacao_rejeita_cadastro_e_preserva_edicao(admin, auth_state, dados, campo):
    novo = criar(admin)
    response = admin.post(API, json=payload(email="outra@empresa.com", **dados) if "email" not in dados else payload(**dados))
    assert response.status_code == 422
    assert any(erro["loc"][1] == campo for erro in response.json()["detail"])
    edicao = admin.put(f"{API}/{novo['id']}", json=payload(**dados))
    assert edicao.status_code == 422
    assert admin.get(f"{API}/{novo['id']}").json() == novo
    assert SENHA not in response.text
    assert "curta" not in edicao.text


def test_rejeita_senha_inicial_ausente_e_vazia(admin):
    dados = payload(senha="")
    assert admin.post(API, json=dados).status_code == 422
    del dados["senha"]
    assert admin.post(API, json=dados).status_code == 422


def test_limites_apos_trim_e_email_254(admin):
    # Domínio/local válidos conforme a mesma validação utilizada no login.
    email = "a" * 64 + "@" + "b" * 63 + "." + "c" * 63 + "." + "d" * 61
    assert len(email) == 254
    novo = criar(admin, nome=" " + "A" * 150 + " ", email=" " + email + " ")
    assert len(novo["nome"]) == 150
    assert novo["email"] == email


@pytest.mark.parametrize("inativo", [False, True])
def test_email_duplicado_em_cadastro_e_edicao(admin, inativo):
    novo = criar(admin)
    outro = criar(admin, email="outro@empresa.com")
    if inativo:
        assert admin.patch(f"{API}/{novo['id']}/status", json={"ativo": False}).status_code == 200
    assert admin.post(API, json=payload(email=" ANA@EMPRESA.COM ")).status_code == 409
    response = admin.put(f"{API}/{outro['id']}", json=payload(email=" ANA@EMPRESA.COM "))
    assert response.status_code == 409
    assert "email" in response.json()["detail"]["campos"]
    assert admin.get(f"{API}/{outro['id']}").json() == outro


def test_desativacao_reativacao_e_troca_senha_invalidam_todas_sessoes(admin, auth_state):
    novo = criar(admin)
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as pessoa, TestClient(auth_state.app, client=("192.0.2.33", 50000)) as outra_sessao:
        assert login(pessoa, novo["email"]).status_code == 200
        assert login(outra_sessao, novo["email"]).status_code == 200
        assert admin.patch(f"{API}/{novo['id']}/status", json={"ativo": False}).status_code == 200
        assert pessoa.get("/api/auth/me").status_code == 401
        assert outra_sessao.get("/api/auth/me").status_code == 401
        assert login(outra_sessao, novo["email"]).status_code == 401
        assert any(not user["ativo"] for user in admin.get(API).json())
        assert admin.patch(f"{API}/{novo['id']}/status", json={"ativo": True}).status_code == 200
        assert pessoa.get("/api/auth/me").status_code == 401
        assert outra_sessao.get("/api/auth/me").status_code == 401
        assert login(pessoa, novo["email"]).status_code == 200
        assert login(outra_sessao, novo["email"]).status_code == 200
        assert admin.put(f"{API}/{novo['id']}", json=payload(senha="NovaSenhaUS32!")).status_code == 200
        assert pessoa.get("/api/auth/me").status_code == 401
        assert outra_sessao.get("/api/auth/me").status_code == 401
        assert login(pessoa, novo["email"]).status_code == 401
        assert login(pessoa, novo["email"], "NovaSenhaUS32!").status_code == 200


def test_exclusao_remove_conta_perfis_e_sessoes(admin, auth_state):
    novo = criar(admin)
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as pessoa:
        assert login(pessoa, novo["email"]).status_code == 200
        assert admin.delete(f"{API}/{novo['id']}").status_code == 204
        assert admin.get(f"{API}/{novo['id']}").status_code == 404
        assert pessoa.get("/api/auth/me").status_code == 401
        assert login(pessoa, novo["email"]).status_code == 401
    with auth_state.engine.connect() as conn:
        for tabela in ("usuarios", "usuario_perfil", "sessoes"):
            assert conn.scalar(text(f"SELECT count(*) FROM {tabela} WHERE id_usuario = :id"), {"id": novo["id"]}) == 0


@pytest.mark.parametrize("vinculo", ["ordens de produção", "planejamentos"])
def test_historico_impede_exclusao_e_preserva_autoria(admin, auth_state, vinculo):
    novo = criar(admin)
    with auth_state.engine.begin() as conn:
        if vinculo == "planejamentos":
            conn.execute(text("INSERT INTO planejamentos (nome, criado_por) VALUES ('Plano', :id)"), {"id": novo["id"]})
            tabela = "planejamentos"
        else:
            produto = conn.scalar(text("INSERT INTO produtos (codigo, nome, unidade) VALUES ('P32', 'Produto', 'UN') RETURNING id_produto"))
            conn.execute(text("INSERT INTO ordens_producao (codigo, produto_id, quantidade, criado_por) VALUES ('OP32', :produto, 1, :id)"), {"id": novo["id"], "produto": produto})
            tabela = "ordens_producao"
    response = admin.delete(f"{API}/{novo['id']}")
    assert response.status_code == 409
    assert vinculo in response.json()["detail"]["vinculos"]
    assert response.json()["detail"]["pode_desativar"] is True
    assert admin.patch(f"{API}/{novo['id']}/status", json={"ativo": False}).status_code == 200
    assert admin.get(f"{API}/{novo['id']}").json()["perfis"] == novo["perfis"]
    with auth_state.engine.connect() as conn:
        assert str(conn.scalar(text(f"SELECT criado_por FROM {tabela}"))) == novo["id"]


@pytest.mark.parametrize("acao", ["excluir", "desativar", "perfil"])
def test_ultimo_admin_ativo_protegido(admin, auth_state, acao):
    # Uma segunda conta administrativa inativa não satisfaz a regra.
    outro = criar(admin, email="inativo@empresa.com", perfis=["ADMINISTRADOR"])
    assert admin.patch(f"{API}/{outro['id']}/status", json={"ativo": False}).status_code == 200
    id = str(auth_state.user_id)
    if acao == "excluir": response = admin.delete(f"{API}/{id}")
    elif acao == "desativar": response = admin.patch(f"{API}/{id}/status", json={"ativo": False})
    else: response = admin.put(f"{API}/{id}", json=payload(email=auth_state.email, perfis=["OPERADOR"]))
    assert response.status_code == 409
    assert "pelo menos um administrador ativo" in response.json()["detail"]
    assert admin.get(f"{API}/{id}").json()["ativo"] is True
    assert "ADMINISTRADOR" in admin.get(f"{API}/{id}").json()["perfis"]


@pytest.mark.parametrize("autenticado", [False, True])
@pytest.mark.parametrize("method,path,body", [
    ("GET", "", None), ("GET", "/{id}", None), ("POST", "", payload()),
    ("PUT", "/{id}", payload()), ("PATCH", "/{id}/status", {"ativo": False}),
    ("PATCH", "/{id}/status", {"ativo": True}), ("DELETE", "/{id}", None),
])
def test_api_requer_administrador(client, auth_state, autenticado, method, path, body):
    if autenticado:
        assert login(client, auth_state.email, auth_state.password).status_code == 200
    response = client.request(method, API + path.format(id=auth_state.user_id), json=body)
    assert response.status_code == (403 if autenticado else 401)
    assert "senha_hash" not in response.text
    with auth_state.engine.connect() as conn:
        assert conn.scalar(text("SELECT ativo FROM usuarios WHERE id_usuario = :id"), {"id": auth_state.user_id}) is True


def simultaneas(app, token, operacoes):
    barreira = Barrier(len(operacoes))
    def executar(item):
        indice, operacao = item
        sessao = token[indice] if isinstance(token, list) else token
        with TestClient(app, client=(f"192.0.2.{40 + indice}", 50000), cookies={"setupflow_session": sessao}) as pessoa:
            barreira.wait(timeout=10)
            method, url, dados = operacao
            return pessoa.request(method, url, json=dados).status_code
    with ThreadPoolExecutor(max_workers=len(operacoes)) as executor:
        return list(executor.map(executar, enumerate(operacoes)))


def test_cadastros_simultaneos_email_unico(admin, auth_state):
    resultados = simultaneas(auth_state.app, admin.cookies["setupflow_session"], [
        ("POST", API, payload(email=email)) for email in ("ana@empresa.com", " ANA@EMPRESA.COM ")
    ])
    assert sorted(resultados) == [201, 409]
    assert sum(user["email"] == "ana@empresa.com" for user in admin.get(API).json()) == 1


@pytest.mark.parametrize("acao", ["excluir", "desativar", "perfil"])
def test_dois_ultimos_admins_em_solicitacoes_simultaneas(admin, auth_state, acao):
    outro = criar(admin, email="segundo@empresa.com", perfis=["ADMINISTRADOR"])
    operacoes = []
    for id, email in ((str(auth_state.user_id), auth_state.email), (outro["id"], outro["email"])):
        if acao == "excluir": operacoes.append(("DELETE", f"{API}/{id}", None))
        elif acao == "desativar": operacoes.append(("PATCH", f"{API}/{id}/status", {"ativo": False}))
        else: operacoes.append(("PUT", f"{API}/{id}", payload(email=email, perfis=["OPERADOR"])))
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as segundo:
        assert login(segundo, outro["email"]).status_code == 200
        resultados = simultaneas(auth_state.app, [admin.cookies["setupflow_session"], segundo.cookies["setupflow_session"]], operacoes)
    assert sorted(resultados) == [204 if acao == "excluir" else 200, 409]
    with auth_state.engine.connect() as conn:
        assert conn.scalar(text("""
            SELECT count(*) FROM usuarios u JOIN usuario_perfil up USING (id_usuario)
            JOIN perfis p USING (id_perfil) WHERE u.ativo AND p.codigo = 'ADMINISTRADOR'
        """)) == 1


def test_script_cria_primeiro_administrador(monkeypatch, auth_state):
    from scripts import create_initial_user
    respostas = iter(["  Admin Inicial  ", " ADMIN@EMPRESA.COM ", "ADMINISTRADOR, OPERADOR"])
    monkeypatch.setattr("builtins.input", lambda _: next(respostas))
    monkeypatch.setattr(create_initial_user, "getpass", lambda _: SENHA)
    monkeypatch.setattr(create_initial_user, "SessionLocal", sessionmaker(bind=auth_state.engine))
    create_initial_user.main()
    with TestClient(auth_state.app, client=("192.0.2.32", 50000)) as pessoa:
        assert login(pessoa, "admin@empresa.com").status_code == 200
        assert sorted(pessoa.get("/api/auth/me").json()["usuario"]["perfis"]) == ["ADMINISTRADOR", "OPERADOR"]
        assert pessoa.post(API, json=payload()).status_code == 201


def test_ids_inexistentes(admin):
    id = uuid4()
    assert admin.get(f"{API}/{id}").status_code == 404
    assert admin.put(f"{API}/{id}", json=payload()).status_code == 404
    assert admin.patch(f"{API}/{id}/status", json={"ativo": False}).status_code == 404
    assert admin.delete(f"{API}/{id}").status_code == 404
