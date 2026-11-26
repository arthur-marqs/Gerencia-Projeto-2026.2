"""Gera a massa Q-07 em um banco PostgreSQL vazio e descartável."""
import json
import os
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.security import hash_password
from app.models.family import Family
from app.models.item_planejamento import ItemPlanejamento
from app.models.maquina import Maquina
from app.models.ordem_producao import OrdemProducao
from app.models.perfil import Perfil
from app.models.planejamento import Planejamento
from app.models.produto import Produto
from app.models.sugestao_planejamento import ItemSugestaoPlanejamento, SugestaoPlanejamento
from app.models.tempo_setup_familia import TempoSetupFamilia
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil

TOTAL_VUS = 10
APROVACOES_POR_VU = 224


def main():
    url = make_url(os.environ["Q07_DATABASE_URL"])
    if (url.get_backend_name() != "postgresql" or url.host not in {"127.0.0.1", "localhost"}
            or url.database != "q07_base_test"):
        raise SystemExit("Use o banco descartável local q07_base_test.")
    saida = Path(os.environ["Q07_MASSA"])
    if saida.exists():
        raise SystemExit("A configuração da massa de destino já existe.")
    engine = create_engine(url)
    prazo = date.today() + timedelta(days=14)
    contas = []
    with Session(engine) as db, db.begin():
        for modelo in (Usuario, OrdemProducao, Family, Maquina, Produto,
                       Planejamento, SugestaoPlanejamento, TempoSetupFamilia):
            if db.scalar(select(func.count()).select_from(modelo)):
                raise SystemExit("O banco da massa precisa estar vazio.")
        perfil = db.scalar(select(Perfil).where(Perfil.codigo == "PLANEJADOR"))
        familias = [Family(code=f"Q07-{letra}", name=f"Família {letra}") for letra in ("A", "B")]
        maquinas = [Maquina(codigo=f"Q07-M{i}", nome=f"Máquina {i}") for i in (1, 2)]
        produtos = [Produto(codigo=f"Q07-P{i}", nome=f"Produto {i}", unidade="UN",
                            family=familias[i % 2], maquinas_compativeis=[maquinas[i // 2]])
                    for i in range(4)]
        db.add_all(familias + maquinas + produtos)
        db.flush()
        db.add_all([
            TempoSetupFamilia(familia_origem_id=familias[a].id,
                              familia_destino_id=familias[b].id, tempo_setup_minutos=minutos)
            for a, b, minutos in [(0, 1, 8), (1, 0, 13)]
        ])
        senha_hash = hash_password(os.environ["Q07_FIXTURE_PASSWORD"])
        for i in range(TOTAL_VUS):
            email = f"planejador-{i + 1}@q07.example.com"
            usuario = Usuario(id_usuario=uuid4(), nome=f"Planejador Q07 {i + 1}", email=email,
                              senha_hash=senha_hash, ativo=True)
            db.add(usuario)
            db.flush()
            db.execute(usuario_perfil.insert().values(id_usuario=usuario.id_usuario,
                                                       id_perfil=perfil.id_perfil))

            def ordem(codigo, produto):
                nova = OrdemProducao(id_ordem=uuid4(), codigo=codigo, produto=produto,
                                    criado_por=usuario.id_usuario, quantidade=10,
                                    duracao_estimada_minutos=25, prazo=prazo, prioridade="Média")
                db.add(nova)
                return nova.id_ordem

            ordens = [ordem(f"Q07-{i}-G-{j}", produto) for j, produto in enumerate(produtos)]
            plano = Planejamento(
                id_planejamento=uuid4(), nome=f"Q07 manual {i}", criado_por=usuario.id_usuario,
                itens=[ItemPlanejamento(ordem_id=oid, posicao=j + 1)
                       for j, oid in enumerate(ordens)],
            )
            db.add(plano)
            aprovacoes = []
            for j in range(APROVACOES_POR_VU):
                oid = ordem(f"Q07-{i}-A-{j}", produtos[0])
                sid = uuid4()
                db.add(SugestaoPlanejamento(
                    id_sugestao=sid, criado_por=usuario.id_usuario,
                    tempo_setup_original_minutos=0, tempo_setup_total_minutos=0,
                    itens=[ItemSugestaoPlanejamento(ordem_id=oid, maquina_id=maquinas[0].id_maquina,
                                                  posicao=1, posicao_original=1, setup_minutos=0)],
                ))
                aprovacoes.append({"sugestao": str(sid), "ordem": str(oid)})
            contas.append({"email": email, "plano": str(plano.id_planejamento),
                           "ordens": list(map(str, ordens)), "aprovacoes": aprovacoes})
    engine.dispose()
    massa = {"usuarios": TOTAL_VUS, "maquinas": 2, "familias": 2, "produtos": 4,
             "ordens": TOTAL_VUS * (4 + APROVACOES_POR_VU), "setups_direcionais": 2,
             "planos_manuais": TOTAL_VUS, "sugestoes_para_aprovacao": TOTAL_VUS * APROVACOES_POR_VU,
             "ordens_por_geracao": 4, "ordens_por_aprovacao": 1, "prazo": prazo.isoformat()}
    saida.write_text(json.dumps({"massa": massa, "contas": contas}), encoding="utf-8")
    print(json.dumps(massa))


if __name__ == "__main__":
    main()
