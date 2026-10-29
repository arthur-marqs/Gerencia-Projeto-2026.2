from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_profiles
from app.models.ordem_producao import OrdemProducao
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.ordem_producao import (
    OrdemProducaoCreate,
    OrdemProducaoResponse,
    OrdemProducaoUpdate,
)


router = APIRouter()


@router.get("", response_model=list[OrdemProducaoResponse])
def listar_ordens_producao(
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    return db.scalars(
        select(OrdemProducao)
        .options(joinedload(OrdemProducao.produto))
        .order_by(OrdemProducao.criado_em.desc(), OrdemProducao.codigo)
    ).all()


@router.get("/{id_ordem}", response_model=OrdemProducaoResponse)
def consultar_ordem_producao(
    id_ordem: UUID,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    ordem = db.get(OrdemProducao, id_ordem)
    if ordem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de produção não encontrada.",
        )
    return ordem


@router.post(
    "",
    response_model=OrdemProducaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_ordem_producao(
    dados: OrdemProducaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    codigo = dados.codigo.strip().upper()
    ordem_existente = db.scalar(
        select(OrdemProducao).where(OrdemProducao.codigo == codigo)
    )
    if ordem_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma ordem de produção com este código.",
        )

    produto = db.get(Produto, dados.produto_id)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    if not produto.ativo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Produto inativo não pode ser utilizado em uma nova ordem.",
        )

    ordem = OrdemProducao(
        codigo=codigo,
        produto_id=produto.id_produto,
        quantidade=dados.quantidade,
        criado_por=usuario.id_usuario,
    )
    db.add(ordem)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar a ordem de produção.",
        ) from erro

    db.refresh(ordem)
    return ordem


@router.put("/{id_ordem}", response_model=OrdemProducaoResponse)
def atualizar_prazo_prioridade_ordem(
    id_ordem: UUID,
    dados: OrdemProducaoUpdate,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    ordem = db.get(OrdemProducao, id_ordem)
    if ordem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de produção não encontrada.",
        )

    ordem.prazo = dados.prazo
    ordem.prioridade = dados.prioridade
    db.commit()
    db.refresh(ordem)
    return ordem
