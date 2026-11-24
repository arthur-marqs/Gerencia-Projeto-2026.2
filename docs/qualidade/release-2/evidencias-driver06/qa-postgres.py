"""Infraestrutura temporária de QA; não faz parte dos testes do produto."""
from pathlib import Path
import subprocess
import tempfile
import sys
import psycopg

BIN = Path('C:/Program Files/PostgreSQL/18/bin')
DATA = Path(tempfile.gettempdir()) / 'setupflow-qa-driver06-16abb60'

def run(name, *args):
    subprocess.run([str(BIN / (name + '.exe')), *args], check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW)

if sys.argv[1] == 'start':
    if DATA.exists():
        raise SystemExit('Diretório já existe: não reutilizar sem inspeção.')
    run('initdb', '-D', str(DATA), '-U', 'qa_driver06', '-A', 'trust',
        '--encoding=UTF8', '--no-locale')
    run('pg_ctl', '-D', str(DATA), '-l', str(DATA / 'server.log'),
        '-o', '-p 55436 -h 127.0.0.1', '-w', 'start')
    with psycopg.connect(host='127.0.0.1', port=55436, user='qa_driver06',
                        dbname='postgres', autocommit=True) as db:
        db.execute('CREATE DATABASE qa_driver06_test')
        print(db.execute('SELECT version()').fetchone()[0])
elif sys.argv[1] == 'stop':
    run('pg_ctl', '-D', str(DATA), '-w', 'stop')
else:
    raise SystemExit('Use start ou stop.')
