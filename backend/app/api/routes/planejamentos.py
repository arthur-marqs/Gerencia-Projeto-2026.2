
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, require_profiles
from app.models.item_planejamento import ItemPlanejamento
from app.models.ordem_producao import OrdemProducao
from app.models.planejamento import Planejamento
from app.models.usuario import Usuario
from app.schemas.planejamento import (
    PlanejamentoCreate,
    PlanejamentoResponse,
    PlanejamentoUpdate,
)


router = APIRouter()


@router.get("", response_model=list[PlanejamentoResponse])
def listar_planejamentos(
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    planejamentos = db.scalars(
        select(Planejamento)
        .options(selectinload(Planejamento.itens))
        .order_by(Planejamento.criado_em.desc())
    ).all()

    return planejamentos


@router.get(
    "/{id_planejamento}",
    response_model=PlanejamentoResponse,
)
def consultar_planejamento(
    id_planejamento: UUID,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    planejamento = db.scalar(
        select(Planejamento)
        .options(selectinload(Planejamento.itens))
        .where(Planejamento.id_planejamento == id_planejamento)
    )

    if planejamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planejamento não encontrado.",
        )

    return planejamento


@router.post(
    "",
    response_model=PlanejamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_planejamento(
    dados: PlanejamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    ordens = list(
        db.scalars(
            select(OrdemProducao).where(
                OrdemProducao.id_ordem.in_(dados.ordens_ids)
            )
        ).all()
    )

    if len(ordens) != len(dados.ordens_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uma ou mais ordens de produção não foram encontradas.",
        )

    if any(ordem.status != "PENDENTE" for ordem in ordens):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Somente ordens pendentes podem ser planejadas.",
        )

    ordem_ja_planejada = db.scalar(
        select(ItemPlanejamento.ordem_id).where(
            ItemPlanejamento.ordem_id.in_(dados.ordens_ids)
        )
    )

    if ordem_ja_planejada is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma ou mais ordens já pertencem a outro planejamento.",
        )

    planejamento = Planejamento(
        nome=dados.nome,
        criado_por=usuario.id_usuario,
    )

    planejamento.itens = [
        ItemPlanejamento(
            ordem_id=ordem_id,
            posicao=posicao,
        )
        for posicao, ordem_id in enumerate(
            dados.ordens_ids,
            start=1,
        )
    ]

    db.add(planejamento)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível criar o planejamento.",
        ) from erro

    planejamento = db.scalar(
        select(Planejamento)
        .options(selectinload(Planejamento.itens))
        .where(
            Planejamento.id_planejamento == planejamento.id_planejamento
        )
    )

    return planejamento


@router.put(
    "/{id_planejamento}",
    response_model=PlanejamentoResponse,
)
def atualizar_planejamento(
    id_planejamento: UUID,
    dados: PlanejamentoUpdate,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    planejamento = db.scalar(
        select(Planejamento)
        .options(selectinload(Planejamento.itens))
        .where(Planejamento.id_planejamento == id_planejamento)
    )

    if planejamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planejamento não encontrado.",
        )

    ordens = list(
        db.scalars(
            select(OrdemProducao).where(
                OrdemProducao.id_ordem.in_(dados.ordens_ids)
            )
        ).all()
    )

    if len(ordens) != len(dados.ordens_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uma ou mais ordens de produção não foram encontradas.",
        )

    if any(ordem.status != "PENDENTE" for ordem in ordens):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Somente ordens pendentes podem ser planejadas.",
        )

    ordem_ja_planejada = db.scalar(
        select(ItemPlanejamento.ordem_id).where(
            ItemPlanejamento.ordem_id.in_(dados.ordens_ids),
            ItemPlanejamento.planejamento_id != id_planejamento,
        )
    )

    if ordem_ja_planejada is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uma ou mais ordens já pertencem a outro planejamento.",
        )

    planejamento.nome = dados.nome

    # Remove os itens antigos antes de inserir a nova sequência.
    planejamento.itens.clear()
    db.flush()

    planejamento.itens = [
        ItemPlanejamento(
            ordem_id=ordem_id,
            posicao=posicao,
        )
        for posicao, ordem_id in enumerate(
            dados.ordens_ids,
            start=1,
        )
    ]

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar o planejamento.",
        ) from erro

    db.expire_all()

    planejamento = db.scalar(
        select(Planejamento)
        .options(selectinload(Planejamento.itens))
        .where(Planejamento.id_planejamento == id_planejamento)
    )

    return planejamento
