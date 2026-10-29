from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_profiles
from app.models.ordem_producao import OrdemProducao
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.ordem_producao import OrdemProducaoCreate, OrdemProducaoResponse


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
