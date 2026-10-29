import json
from hashlib import sha256
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_profiles
from app.models.ordem_producao import OrdemProducao
from app.models.ordem_producao_operacao import OrdemProducaoOperacao
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.schemas.ordem_producao import OrdemProducaoCreate, OrdemProducaoResponse


router = APIRouter()


def _hash_conteudo(dados: OrdemProducaoCreate) -> str:
    conteudo = json.dumps(
        {
            "codigo": dados.codigo.strip().upper(),
            "produto_id": str(dados.produto_id),
            "quantidade": format(dados.quantidade.normalize(), "f"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(conteudo.encode("utf-8")).hexdigest()


def _buscar_ordem_reutilizada(
    db: Session,
    usuario_id: UUID,
    chave: UUID,
    hash_conteudo: str,
) -> OrdemProducao | None:
    operacao = db.scalar(
        select(OrdemProducaoOperacao)
        .options(joinedload(OrdemProducaoOperacao.ordem))
        .where(
            OrdemProducaoOperacao.usuario_id == usuario_id,
            OrdemProducaoOperacao.chave == chave,
        )
    )
    if operacao is None:
        return None

    if operacao.hash_conteudo != hash_conteudo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A chave de idempotência já foi utilizada com outro conteúdo.",
        )
    if operacao.ordem is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A operação de cadastro não possui uma ordem associada.",
        )

    return operacao.ordem


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
    response: Response,
    idempotency_key: UUID = Header(alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    codigo = dados.codigo.strip().upper()
    hash_conteudo = _hash_conteudo(dados)
    ordem_reutilizada = _buscar_ordem_reutilizada(
        db,
        usuario.id_usuario,
        idempotency_key,
        hash_conteudo,
    )
    if ordem_reutilizada is not None:
        response.status_code = status.HTTP_200_OK
        return ordem_reutilizada

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
    operacao = OrdemProducaoOperacao(
        usuario_id=usuario.id_usuario,
        chave=idempotency_key,
        hash_conteudo=hash_conteudo,
    )
    db.add(operacao)

    try:
        db.flush()
    except IntegrityError as erro:
        db.rollback()
        ordem_reutilizada = _buscar_ordem_reutilizada(
            db,
            usuario.id_usuario,
            idempotency_key,
            hash_conteudo,
        )
        if ordem_reutilizada is not None:
            response.status_code = status.HTTP_200_OK
            return ordem_reutilizada
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar a ordem de produção.",
        ) from erro

    ordem.operacao_id = operacao.id_operacao
    db.add(ordem)

    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        ordem_reutilizada = _buscar_ordem_reutilizada(
            db,
            usuario.id_usuario,
            idempotency_key,
            hash_conteudo,
        )
        if ordem_reutilizada is not None:
            response.status_code = status.HTTP_200_OK
            return ordem_reutilizada
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar a ordem de produção.",
        ) from erro

    db.refresh(ordem)
    return ordem
