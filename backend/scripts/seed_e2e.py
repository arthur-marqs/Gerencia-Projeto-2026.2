"""Fixtures da US-32 para Cypress. Recusa qualquer banco sem sufixo _e2e_test.

Uso: E2E_DATABASE_URL=... python -m scripts.seed_e2e [normal|vazio|bootstrap]
Não é importado pela aplicação nem expõe endpoints de preparação de dados.
"""
import contextlib
import io
import json
import os
import sys
from unittest.mock import patch

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
import app.models  # noqa: F401 — registra os modelos para a limpeza das fixtures
from app.core.security import hash_password
from app.models.item_planejamento import ItemPlanejamento
from app.models.ordem_producao import OrdemProducao
from app.models.perfil import Perfil
from app.models.planejamento import Planejamento
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil

SENHA = 'SenhaE2E!2026'
CONTAS = {
    'admin': ('Administrador E2E', 'admin.e2e@example.com', ['ADMINISTRADOR', 'PLANEJADOR']),
    'ana': ('Ana E2E', 'ana.e2e@example.com', ['PLANEJADOR']),
    'operador': ('Operador E2E', 'operador.e2e@example.com', ['OPERADOR']),
    'inativo': ('Inativo E2E', 'inativo.e2e@example.com', ['OPERADOR']),
    'exclusao': ('Conta Exclusão E2E', 'exclusao.e2e@example.com', ['OPERADOR']),
    'autor_ordem': ('Autor Ordem E2E', 'autor.ordem.e2e@example.com', ['PLANEJADOR']),
    'autor_plano': ('Autor Plano E2E', 'autor.plano.e2e@example.com', ['PLANEJADOR']),
}


def preparar(modo):
    valor = os.environ.get('E2E_DATABASE_URL', '')
    if not valor:
        raise SystemExit('Defina E2E_DATABASE_URL para um banco exclusivo terminado em _e2e_test.')
    try:
        url = make_url(valor)
    except ArgumentError:
        raise SystemExit('E2E_DATABASE_URL deve ser uma URL SQLAlchemy válida.') from None
    if url.get_backend_name() != 'postgresql' or not (url.database or '').endswith('_e2e_test'):
        raise SystemExit('Preparação recusada: use PostgreSQL com banco terminado em _e2e_test.')
    engine = create_engine(url.set(drivername='postgresql+psycopg'))
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        if modo == 'inspecionar':
            with factory() as db:
                usuarios = [
                    {'id': str(u.id_usuario), 'nome': u.nome, 'email': u.email, 'ativo': u.ativo,
                     'perfis': list(db.scalars(select(Perfil.codigo).join(usuario_perfil)
                                 .where(usuario_perfil.c.id_usuario == u.id_usuario).order_by(Perfil.codigo)))}
                    for u in db.scalars(select(Usuario).order_by(Usuario.email))
                ]
                ordem = db.scalar(select(OrdemProducao).where(OrdemProducao.codigo == 'OP-E2E'))
                plano = db.scalar(select(Planejamento).where(Planejamento.nome == 'Plano E2E'))
                return {'usuarios': usuarios,
                        'ordem': {'id': str(ordem.id_ordem), 'criado_por': str(ordem.criado_por)} if ordem else None,
                        'plano': {'id': str(plano.id_planejamento), 'criado_por': str(plano.criado_por)} if plano else None}
        if modo == 'bootstrap':
            from scripts import create_initial_user
            saida = io.StringIO()
            respostas = ['Administrador E2E', 'admin.e2e@example.com', 'ADMINISTRADOR, PLANEJADOR']
            with patch('builtins.input', side_effect=respostas), \
                    patch.object(create_initial_user, 'getpass', return_value=SENHA), \
                    patch.object(create_initial_user, 'SessionLocal', factory), \
                    contextlib.redirect_stdout(saida):
                create_initial_user.main()
            return {'mensagem': saida.getvalue().strip()}

        with factory.begin() as db:
            tabelas = ', '.join(f'"{tabela.name}"' for tabela in Base.metadata.sorted_tables
                                if tabela.name != 'perfis')
            db.execute(text(f'TRUNCATE TABLE {tabelas} CASCADE'))
            perfis = {perfil.codigo: perfil.id_perfil for perfil in db.scalars(select(Perfil))}
            if not {'ADMINISTRADOR', 'PLANEJADOR', 'OPERADOR'} <= perfis.keys():
                raise SystemExit('Aplique alembic upgrade head no banco E2E antes de preparar os dados.')
            if modo == 'vazio':
                return {'usuarios': {}}
            senha_hash = hash_password(SENHA)
            usuarios = {}
            for chave, (nome, email, codigos) in CONTAS.items():
                usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, ativo=chave != 'inativo')
                db.add(usuario)
                db.flush()
                db.execute(usuario_perfil.insert(), [
                    {'id_usuario': usuario.id_usuario, 'id_perfil': perfis[codigo]} for codigo in codigos
                ])
                usuarios[chave] = {'id': str(usuario.id_usuario), 'nome': nome, 'email': email,
                                   'perfis': codigos, 'ativo': usuario.ativo}
            produto = Produto(codigo='PROD-E2E', nome='Produto E2E', unidade='UN')
            db.add(produto)
            db.flush()
            ordem = OrdemProducao(codigo='OP-E2E', produto_id=produto.id_produto, quantidade=10,
                                  criado_por=usuarios['autor_ordem']['id'])
            plano = Planejamento(nome='Plano E2E', criado_por=usuarios['autor_plano']['id'])
            db.add_all([ordem, plano])
            db.flush()
            db.add(ItemPlanejamento(ordem_id=ordem.id_ordem, planejamento_id=plano.id_planejamento, posicao=1))
            return {'usuarios': usuarios, 'ordem_id': str(ordem.id_ordem),
                    'planejamento_id': str(plano.id_planejamento)}
    finally:
        engine.dispose()


if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else 'normal'
    if modo not in {'normal', 'vazio', 'bootstrap', 'inspecionar'}:
        raise SystemExit('Modo inválido; use normal, vazio, bootstrap ou inspecionar.')
    print(json.dumps(preparar(modo), ensure_ascii=False))
