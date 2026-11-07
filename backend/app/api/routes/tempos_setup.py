from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_profiles
from app.models.family import Family
from app.models.tempo_setup_familia import TempoSetupFamilia
from app.models.usuario import Usuario
from app.schemas.tempo_setup_familia import (
    TempoSetupFamiliaCreate,
    TempoSetupFamiliaResponse,
)


router = APIRouter(prefix="/tempos-setup", tags=["Tempos de setup entre famílias"])


@router.get("", response_model=list[TempoSetupFamiliaResponse])
def listar_tempos_setup(
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(TempoSetupFamilia)
        .options(
            joinedload(TempoSetupFamilia.familia_origem),
            joinedload(TempoSetupFamilia.familia_destino),
        )
        .order_by(TempoSetupFamilia.criado_em.desc())
    ).all()


@router.post(
    "",
    response_model=TempoSetupFamiliaResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_tempo_setup(
    dados: TempoSetupFamiliaCreate,
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
    db: Session = Depends(get_db),
):
    familia_origem = db.get(Family, dados.familia_origem_id)
    if familia_origem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Família de origem não encontrada.",
        )

    familia_destino = db.get(Family, dados.familia_destino_id)
    if familia_destino is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Família de destino não encontrada.",
        )

    existente = db.scalar(
        select(TempoSetupFamilia).where(
            TempoSetupFamilia.familia_origem_id == dados.familia_origem_id,
            TempoSetupFamilia.familia_destino_id == dados.familia_destino_id,
        )
    )
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um tempo de setup configurado entre essas famílias.",
        )

    tempo_setup = TempoSetupFamilia(
        familia_origem_id=dados.familia_origem_id,
        familia_destino_id=dados.familia_destino_id,
        tempo_setup_minutos=dados.tempo_setup_minutos,
    )
    db.add(tempo_setup)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar o tempo de setup para essa combinação de famílias.",
        ) from erro

    db.refresh(tempo_setup)
    return tempo_setup
