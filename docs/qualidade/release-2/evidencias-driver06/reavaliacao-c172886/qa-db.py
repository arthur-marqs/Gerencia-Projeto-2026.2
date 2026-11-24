"""Tarefas exclusivas para o banco E2E desta reavaliação; nunca usar em produção."""
from pathlib import Path
import json
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'backend/app').is_dir())
sys.path.insert(0, str(ROOT / 'backend'))
url = make_url(os.environ['E2E_DATABASE_URL'])
assert url.database == 'qa_driver06_browser_e2e_test'
assert url.host == '127.0.0.1' and url.port == 55437
if sys.argv[1] == 'reset':
    from scripts.seed_e2e import preparar
    preparar('normal')
    print(json.dumps({'reset': True}))
else:
    engine = create_engine(url)
    with engine.begin() as db:
        if sys.argv[1] == 'expirar':
            result = db.execute(text("""UPDATE sessoes SET criada_em=now()-interval '2 days',
                expira_em=now()-interval '1 day' WHERE invalidada_em IS NULL"""))
        elif sys.argv[1] == 'invalidar':
            result = db.execute(text('UPDATE sessoes SET invalidada_em=now() WHERE invalidada_em IS NULL'))
        else:
            raise SystemExit('Modo inválido')
        print(json.dumps({'sessoes_alteradas': result.rowcount}))
    engine.dispose()
