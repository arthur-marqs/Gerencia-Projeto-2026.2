from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_profiles
from app.models.family import Family
from app.models.usuario import Usuario
from app.schemas.family import FamilyCreate, FamilyRead


router = APIRouter(prefix="/families", tags=["Famílias de produtos"])


@router.get("", response_model=list[FamilyRead])
def listar_familias(
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
    db: Session = Depends(get_db),
):
    return db.scalars(select(Family).order_by(Family.name, Family.code)).all()


@router.post(
    "",
    response_model=FamilyRead,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_familia(
    dados: FamilyCreate,
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
    db: Session = Depends(get_db),
):
    existente = db.scalar(select(Family).where(Family.code == dados.code))
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma família cadastrada com este código.",
        )

    familia = Family(
        code=dados.code,
        name=dados.name,
        description=dados.description,
    )
    db.add(familia)

    try:
        db.commit()
    except IntegrityError as exc:
        # A constraint única também cobre dois cadastros simultâneos do mesmo código.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma família cadastrada com este código.",
        ) from exc

    db.refresh(familia)
    return familia
