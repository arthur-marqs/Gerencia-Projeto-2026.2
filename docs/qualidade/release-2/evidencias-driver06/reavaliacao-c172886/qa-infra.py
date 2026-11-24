"""Infraestrutura isolada da reavaliação; executar na raiz do repositório."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import psycopg

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'backend/app').is_dir())
DATA = Path(tempfile.gettempdir()) / 'setupflow-qa-driver06-c172886'
BIN = Path('C:/Program Files/PostgreSQL/18/bin')
def run(name, *args):
    subprocess.run([str(BIN / (name + '.exe')), *args], check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW)
if sys.argv[1] == 'start':
    if DATA.exists():
        raise SystemExit('Diretório já existe; não sobrescrever.')
    run('initdb', '-D', str(DATA), '-U', 'qa_driver06', '-A', 'trust', '--encoding=UTF8', '--no-locale')
    run('pg_ctl', '-D', str(DATA), '-l', str(DATA / 'server.log'), '-o', '-p 55437 -h 127.0.0.1', '-w', 'start')
    with psycopg.connect(host='127.0.0.1', port=55437, user='qa_driver06', dbname='postgres', autocommit=True) as db:
        for name in ['qa_driver06_test', 'qa_driver06_browser_e2e_test']:
            db.execute(psycopg.sql.SQL('CREATE DATABASE {}').format(psycopg.sql.Identifier(name)))
        print(db.execute('SELECT version()').fetchone()[0])
elif sys.argv[1] == 'stop':
    run('pg_ctl', '-D', str(DATA), '-w', 'stop')
else:
    raise SystemExit('Use start ou stop')
