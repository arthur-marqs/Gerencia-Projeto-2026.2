"""Ensaio de QA avulso. Execute a partir de backend com PostgreSQL descartável."""

import json
import os
import socket
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Thread
from time import monotonic, sleep
from uuid import uuid4

import httpx
import psycopg
import uvicorn
from alembic import command
from alembic.config import Config
from psycopg.rows import dict_row
from sqlalchemy import event
from sqlalchemy.engine import make_url


def main():
    url = make_url(os.environ["TEST_DATABASE_URL"])
    if url.host != "127.0.0.1" or not (url.database or "").endswith("_test"):
        raise SystemExit("Use um banco PostgreSQL descartável em 127.0.0.1, terminado em _test.")
    os.environ.update(
        DB_HOST=url.host,
        DB_PORT=str(url.port or 5432),
        DB_NAME=url.database,
        DB_USER=url.username,
        DB_PASSWORD=url.password or "",
        COOKIE_SECURE="false",
    )
    dsn = url.set(drivername="postgresql").render_as_string(hide_password=False)

    def connect():
        return psycopg.connect(dsn, row_factory=dict_row, autocommit=True)

    # A conta local precisa encerrar outra conexão da própria conta.
    command.upgrade(Config("alembic.ini"), "head")
    from app.core.security import hash_password
    from app.db.session import engine
    from app.main import app

    run = uuid4().hex[:8]
    email = f"driver01-{run}@example.test"
    password = "Senha descartável do ensaio QA!2026"
    with connect() as db:
        pg_version = db.execute("SHOW server_version").fetchone()["server_version"]
        user = db.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, ativo) "
            "VALUES ('Planejador de teste', %s, %s, true) RETURNING id_usuario",
            (email, hash_password(password)),
        ).fetchone()["id_usuario"]
        db.execute(
            "INSERT INTO usuario_perfil (id_usuario, id_perfil) "
            "SELECT %s, id_perfil FROM perfis WHERE codigo = 'PLANEJADOR'",
            (user,),
        )

    print(json.dumps({
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "data_hora": datetime.now().astimezone().isoformat(),
        "banco": url.database,
        "postgresql": pg_version,
        "tecnica": "HTTP em Uvicorn, sessão real da API e pg_terminate_backend após DML",
        "execucao": run,
    }), flush=True)

    fault = {}

    @event.listens_for(engine, "after_cursor_execute")
    def disconnect(conn, cursor, statement, *_args):
        prefix = fault.get("prefixo_sql")
        if not prefix or "pid" in fault or not statement.lower().startswith(prefix):
            return
        assert cursor.rowcount == 1, (statement, cursor.rowcount)
        pid = conn.connection.driver_connection.info.backend_pid
        with connect() as db:
            stopped = db.execute(
                "SELECT pg_terminate_backend(%s, 4000) AS encerrada", (pid,)
            ).fetchone()["encerrada"]
        fault.update(pid=pid, linhas_escritas=cursor.rowcount, sessao_encerrada=stopped)
        assert stopped, pid

    @event.listens_for(engine, "handle_error")
    def observe_disconnect(context):
        if "pid" in fault and "erro_do_driver" not in fault:
            error = context.original_exception
            fault.update(erro_do_driver=type(error).__name__,
                         sqlstate=getattr(error, "sqlstate", None),
                         desconexao=context.is_disconnect)

    def snapshot():
        with connect() as db:
            return {
                "ordens": db.execute(
                    "SELECT * FROM ordens_producao ORDER BY id_ordem"
                ).fetchall(),
                "chaves": db.execute(
                    "SELECT * FROM ordens_producao_operacoes ORDER BY id_operacao"
                ).fetchall(),
                "produto": db.execute(
                    "SELECT * FROM produtos WHERE id_produto = %s", (product,)
                ).fetchone(),
            }

    def request(method, path, payload, expected, **kwargs):
        response = http.request(method, path, json=payload, **kwargs)
        assert response.status_code == expected, (method, path, response.status_code, response.text)
        return response.json()

    def consulta(order):
        return request("GET", f"{orders}/{order}", None, 200)

    def cadastro(code, amount):
        return {"codigo": code, "produto_id": product, "quantidade": amount}

    def confirmar(method, path, payload, headers, expected, order=None):
        result = request(method, path, payload, expected, headers=headers)
        assert order is None or result["id_ordem"] == order
        order = result["id_ordem"]
        assert consulta(order) == result
        rows = snapshot()
        persisted = next(row for row in rows["ordens"] if str(row["id_ordem"]) == order)
        for key, value in payload.items():
            assert str(persisted[key]) == str(value) or persisted[key] == value, (key, persisted, value)
        if method == "POST":
            keys = [row for row in rows["chaves"] if str(row["chave"]) == headers["Idempotency-Key"]]
            assert len(keys) == 1 and keys[0]["id_operacao"] == persisted["operacao_id"]
            assert keys[0]["usuario_id"] == user == persisted["criado_por"]
        return order

    orders = "/api/ordens-producao"
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level="warning"))
        thread = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            deadline = monotonic() + 10
            while not server.started and thread.is_alive() and monotonic() < deadline:
                sleep(0.02)
            assert server.started
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10) as http:
                request("POST", "/api/auth/login", {"email": email, "password": password}, 200)
                product = request("POST", "/api/produtos", {
                    "codigo": f"PROD-{run}", "nome": "Produto de QA", "unidade": "un"
                }, 201)["id_produto"]
                headers = {"Idempotency-Key": str(uuid4())}
                order = confirmar("POST", orders, cadastro(f"BASE-{run}".upper(), 1), headers, 201)
                edit = f"{orders}/{order}"
                duration = f"{edit}/duracao-estimada"
                confirmar("PATCH", duration, {"duracao_estimada_minutos": 30}, {}, 200, order)
                due = lambda offset: (date.today() + timedelta(days=offset)).isoformat()
                confirmar("PUT", edit, {"prazo": due(7), "prioridade": "Média"}, {}, 200, order)
                print(json.dumps({"caso": "CT-128", "ordem": order, "resultado": "3/3 (POST, PATCH, PUT)"}), flush=True)

                for i in range(1, 21):
                    is_create = i <= 10
                    is_duration = 11 <= i <= 15
                    case = (f"CT-126-{i:02}" if is_create else f"CT-127-{i-10:02}")
                    if is_create:
                        prefix = "insert into ordens_producao_operacoes " if i <= 5 else "insert into ordens_producao "
                        method, path, payload, expected = "POST", orders, cadastro(f"QA-{run}-{i:02}".upper(), i + 1), 201
                        headers = {"Idempotency-Key": str(uuid4())}
                    elif is_duration:
                        method, path, payload, expected = "PATCH", duration, {"duracao_estimada_minutos": i * 5}, 200
                        headers, prefix = {}, "update ordens_producao "
                    else:
                        method, path, payload, expected = "PUT", edit, {"prazo": due(i), "prioridade": "Alta" if i % 2 else "Baixa"}, 200
                        headers, prefix = {}, "update ordens_producao "

                    before = snapshot()
                    previous = consulta(order)
                    fault.update(prefixo_sql=prefix)
                    response = http.request(method, path, json=payload, headers=headers)
                    event_data = fault.copy()
                    fault.clear()
                    unchanged = before == snapshot() and consulta(order) == previous
                    detail = response.json().get("detail", "")
                    error_ok = response.status_code == 503 and "confirmar a gravação" in detail
                    evidence = {"caso": case, "metodo": method, "rota": path,
                                "dados": payload, "chave": headers.get("Idempotency-Key"),
                                "antes": {key: previous[key] for key in ("duracao_estimada_minutos", "prazo", "prioridade")},
                                "falha": event_data, "http": response.status_code,
                                "mensagem": detail, "estado_preservado": unchanged}
                    if not (event_data.get("sessao_encerrada") and event_data.get("desconexao") and error_ok and unchanged):
                        print(json.dumps(evidence, ensure_ascii=False), flush=True)
                        raise AssertionError(case)
                    saved = confirmar(method, path, payload, headers, expected, None if is_create else order)
                    evidence.update(recuperacao_http=expected, consulta_independente_http=200, id_apos_recuperacao=saved)
                    print(json.dumps(evidence, ensure_ascii=False), flush=True)
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            engine.dispose()


if __name__ == "__main__":
    main()
