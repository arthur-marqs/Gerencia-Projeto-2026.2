from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_profiles
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.maquina import (
    MaquinaCreate,
    MaquinaResponse,
    MaquinaStatusUpdate,
    MaquinaUpdate,
)


router = APIRouter()


@router.get(
    "",
    response_model=list[MaquinaResponse],
)
def listar_maquinas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    return db.scalars(select(Maquina).order_by(Maquina.codigo)).all()


@router.post(
    "",
    response_model=MaquinaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_maquina(
    dados: MaquinaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    codigo = dados.codigo.strip().upper()
    nome = dados.nome.strip()

    maquina_existente = db.scalar(
        select(Maquina).where(Maquina.codigo == codigo)
    )

    if maquina_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma máquina com este código.",
        )

    maquina = Maquina(
        codigo=codigo,
        nome=nome,
        descricao=dados.descricao,
    )
    db.add(maquina)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar a máquina.",
        )

    db.refresh(maquina)
    return maquina


@router.put(
    "/{id_maquina}",
    response_model=MaquinaResponse,
)
def atualizar_maquina(
    id_maquina: UUID,
    dados: MaquinaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    maquina = db.get(Maquina, id_maquina)
    if maquina is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Máquina não encontrada.",
        )

    codigo = dados.codigo.upper()
    maquina_com_codigo = db.scalar(
        select(Maquina).where(
            Maquina.codigo == codigo,
            Maquina.id_maquina != id_maquina,
        )
    )
    if maquina_com_codigo is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma máquina com este código.",
        )

    maquina.codigo = codigo
    maquina.nome = dados.nome
    maquina.descricao = dados.descricao

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar a máquina.",
        )

    db.refresh(maquina)
    return maquina


@router.patch(
    "/{id_maquina}/status",
    response_model=MaquinaResponse,
)
def atualizar_status_maquina(
    id_maquina: UUID,
    dados: MaquinaStatusUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    maquina = db.get(Maquina, id_maquina)
    if maquina is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Máquina não encontrada.",
        )

    maquina.ativo = dados.ativo
    db.commit()
    db.refresh(maquina)
    return maquina


@router.delete(
    "/{id_maquina}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_maquina(
    id_maquina: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    maquina = db.get(Maquina, id_maquina)
    if maquina is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Máquina não encontrada.",
        )

    db.delete(maquina)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        codigo_erro = getattr(erro.orig, "sqlstate", None) or getattr(
            erro.orig, "pgcode", None
        )
        if codigo_erro in {"23503", "23001"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A máquina possui registros vinculados e não pode ser "
                    "excluída. Inative-a para mantê-la fora de novos "
                    "planejamentos."
                ),
            ) from erro
        raise
