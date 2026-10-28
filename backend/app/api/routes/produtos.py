from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_profiles
from app.models.family import Family
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.produto import (
    ProdutoCreate,
    ProdutoFamiliaUpdate,
    ProdutoResponse,
)


router = APIRouter()


@router.get(
    "",
    response_model=list[ProdutoResponse],
)
def listar_produtos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    produtos = db.scalars(
        select(Produto).order_by(Produto.codigo)
    ).all()

    return produtos


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    codigo = dados.codigo.strip().upper()
    nome = dados.nome.strip()
    unidade = dados.unidade.strip()

    produto_existente = db.scalar(
        select(Produto).where(Produto.codigo == codigo)
    )

    if produto_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com este código.",
        )

    produto = Produto(
        codigo=codigo,
        nome=nome,
        unidade=unidade,
    )

    db.add(produto)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar o produto.",
        )

    db.refresh(produto)

    return produto


@router.patch(
    "/{produto_id}/familia",
    response_model=ProdutoResponse,
)
def associar_produto_familia(
    produto_id: UUID,
    dados: ProdutoFamiliaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    produto = db.get(Produto, produto_id)

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    if dados.family_id is not None:
        familia = db.get(Family, dados.family_id)

        if familia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Família não encontrada.",
            )

    produto.family_id = dados.family_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível associar o produto à família.",
        )

    db.refresh(produto)

    return produto
