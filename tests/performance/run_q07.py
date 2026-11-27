"""Executa a Q-07 localmente, a partir de PostgreSQL isolado e vazio."""
import argparse
import csv
import json
import os
import platform
import secrets
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import psycopg
from psycopg import sql

HERE = Path(__file__).resolve().parent
FUSO = ZoneInfo("America/Sao_Paulo")


def timestamp():
    return datetime.now(FUSO).isoformat(timespec="seconds")


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def samples(raw, output):
    if not raw.exists():
        return
    with raw.open(encoding="utf-8") as origem, output.open("w", newline="", encoding="utf-8") as destino:
        writer = csv.writer(destino)
        writer.writerow(["operacao", "amostra", "duracao_ms"])
        counts = {}
        for line in origem:
            row = json.loads(line)
            if row.get("type") != "Point" or not row["metric"].startswith("q07_") or not row["metric"].endswith("_ms"):
                continue
            operation = row["metric"][4:-3]
            counts[operation] = counts.get(operation, 0) + 1
            writer.writerow([operation, counts[operation], row["data"]["value"]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--k6", default="k6")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--estado", required=True)
    args = parser.parse_args()
    backend = args.backend.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True)
    fixture = secrets.token_urlsafe(24)
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_port = int(os.environ.get("DB_PORT", "55484"))
    api_port = 8017
    env = dict(os.environ, DB_HOST="127.0.0.1", DB_PORT=str(db_port), DB_NAME="q07_base_test",
               COOKIE_SECURE="false", Q07_FIXTURE_PASSWORD=fixture, PYTHONUTF8="1",
               PYTHONDONTWRITEBYTECODE="1", K6_NO_USAGE_REPORT="true")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(backend), env.get("PYTHONPATH")]))
    env["Q07_DATABASE_URL"] = (
        f"postgresql+psycopg://{quote(db_user, safe='')}:{quote(db_password, safe='')}"
        f"@127.0.0.1:{db_port}/q07_base_test"
    )
    env["Q07_MASSA"] = str(out / "massa-privada.json")
    env["Q07_API"] = f"http://127.0.0.1:{api_port}"
    manifest = {
        "inicio": timestamp(), "fuso": "America/Sao_Paulo", "commit": args.commit,
        "branch": args.branch, "alteracoes_locais": args.estado, "sistema": platform.platform(),
        "cpu_logicas": os.cpu_count(), "python": platform.python_version(),
        "api": {"host": "127.0.0.1", "porta": api_port, "uvicorn_workers": 1,
                "cookie_secure": False, "log_de_acesso": False},
        "gerador_na_mesma_maquina": True, "execucoes": [],
    }

    def flush():
        save_json(out / "manifesto.json", manifest)

    def run(name, cmd, runtime=env):
        print(f"{timestamp()} {name}: início", flush=True)
        start = timestamp()
        clock = time.monotonic()
        result = subprocess.run(cmd, cwd=backend, env=runtime, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        log = (result.stdout + result.stderr).replace(db_password, "<sigilo>").replace(fixture, "<sigilo>")
        (out / f"{name}.log").write_text(log, encoding="utf-8")
        manifest["execucoes"].append({
            "nome": name, "comando": [Path(cmd[0]).name, *cmd[1:]], "inicio": start,
            "fim": timestamp(), "duracao_s": round(time.monotonic() - clock, 3),
            "codigo": result.returncode, "log": f"{name}.log",
        })
        flush()
        print(f"{timestamp()} {name}: saída {result.returncode}", flush=True)
        return result.returncode

    def with_api(nome_db, fn):
        with socket.socket() as check:
            check.bind(("127.0.0.1", api_port))
        config = dict(env, DB_NAME=nome_db)
        app_log = out / f"api-{nome_db}.log"
        command = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
                   "--port", str(api_port), "--workers", "1", "--no-access-log"]
        start = timestamp()
        with app_log.open("w", encoding="utf-8") as log:
            proc = subprocess.Popen(command, cwd=backend, env=config, stdout=log, stderr=subprocess.STDOUT)
            try:
                for _ in range(60):
                    if proc.poll() is not None:
                        raise RuntimeError("A API encerrou antes de responder.")
                    try:
                        with urlopen(env["Q07_API"] + "/api/health", timeout=1) as response:
                            if response.status == 200:
                                break
                    except (URLError, TimeoutError):
                        time.sleep(0.5)
                else:
                    raise RuntimeError("A API não ficou disponível no loopback.")
                return fn(config)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                try:
                    code = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    code = proc.wait()
                manifest["execucoes"].append({
                    "nome": f"api-{nome_db}", "comando": [Path(command[0]).name, *command[1:]],
                    "inicio": start, "fim": timestamp(), "codigo": code,
                    "observacao": "Processo encerrado ao final da fase.", "log": app_log.name,
                })
                flush()

    def phase(fase, vus, config):
        nome = f"{fase}-{vus}-vus"
        raw = out / f"raw-{nome}.json"
        code = run(nome, [args.k6, "run", "--out", f"json={raw}", str(HERE / "q07.js")],
                   dict(config, Q07_FASE=fase, Q07_VUS=str(vus),
                        Q07_SUMMARY=str(out / f"resultados-{nome}.json")))
        samples(raw, out / f"amostras-{nome}.csv")
        return code

    rc = 1
    try:
        with psycopg.connect(host="127.0.0.1", port=db_port, dbname="postgres",
                             user=db_user, password=db_password, autocommit=True) as conn:
            manifest["postgresql"] = {
                "versao": conn.execute("SHOW server_version").fetchone()[0],
                "max_connections": conn.execute("SHOW max_connections").fetchone()[0],
                "shared_buffers": conn.execute("SHOW shared_buffers").fetchone()[0],
                "porta": db_port,
            }
            for name, command in [
                ("k6-versao", [args.k6, "version"]),
                ("migracao", [sys.executable, "-m", "alembic", "upgrade", "head"]),
                ("massa", [sys.executable, str(HERE / "seed_q07.py")]),
            ]:
                if run(name, command):
                    return 1
            with Path(env["Q07_MASSA"]).open(encoding="utf-8") as arquivo:
                manifest["massa"] = json.load(arquivo)["massa"]
            for db in ("q07_smoke_test", "q07_5_test", "q07_10_test"):
                conn.execute(sql.SQL("CREATE DATABASE {} TEMPLATE q07_base_test").format(sql.Identifier(db)))
            flush()
        if with_api("q07_smoke_test", lambda cfg: phase("smoke", 1, cfg)):
            manifest["impedimento"] = "A verificação inicial falhou. Rodadas oficiais não iniciadas."
            return 1

        def round_for(cfg, vus):
            warm = phase("aquecimento", vus, cfg)
            measured = phase("medicao", vus, cfg)
            return warm or measured

        results = [with_api(f"q07_{vus}_test", lambda cfg, vus=vus: round_for(cfg, vus))
                   for vus in (5, 10)]
        rc = int(any(results))
        return rc
    except Exception as error:
        manifest["impedimento"] = type(error).__name__
        raise
    finally:
        manifest["fim"] = timestamp()
        manifest["codigo"] = rc
        flush()


if __name__ == "__main__":
    raise SystemExit(main())
