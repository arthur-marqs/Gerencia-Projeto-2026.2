from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_profiles
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.maquina import MaquinaCreate, MaquinaResponse


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
