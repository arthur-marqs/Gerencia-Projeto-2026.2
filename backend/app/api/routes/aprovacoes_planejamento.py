from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import get_db, require_profiles
from app.models.aprovacao_planejamento import AprovacaoPlanejamento, ItemAprovacaoPlanejamento
from app.models.item_planejamento import ItemPlanejamento
from app.models.maquina import Maquina
from app.models.ordem_producao import OrdemProducao
from app.models.planejamento import Planejamento
from app.models.produto_maquina import produto_maquina
from app.models.sugestao_planejamento import ItemSugestaoPlanejamento, SugestaoPlanejamento
from app.models.usuario import Usuario
from app.schemas.aprovacao_planejamento import (
    AprovacaoPlanejamentoCreate,
    AprovacaoPlanejamentoResponse,
    CandidatoAprovacaoResponse,
)

router = APIRouter(prefix="/aprovacoes")

SEM_PLANEJAMENTO = "Não existe planejamento disponível para aprovação."
ORDENS_JA_APROVADAS = "Uma ou mais ordens já fazem parte de um planejamento aprovado."
SUGESTAO_INDISPONIVEL = (
    "A sugestão ficou indisponível para aprovação. "
    "Gere uma sequência sugerida atualizada."
)
ITENS_MANUAIS = selectinload(Planejamento.itens).joinedload(ItemPlanejamento.ordem)
ITENS_SUGERIDOS = selectinload(SugestaoPlanejamento.itens).options(
    joinedload(ItemSugestaoPlanejamento.ordem),
    joinedload(ItemSugestaoPlanejamento.maquina),
)
ITENS_APROVADOS = selectinload(AprovacaoPlanejamento.itens).options(
    joinedload(ItemAprovacaoPlanejamento.ordem),
    joinedload(ItemAprovacaoPlanejamento.maquina),
)


def _vinculos_com_maquinas_ativas():
    return (
        select(produto_maquina.c.id_maquina)
        .join(Maquina, Maquina.id_maquina == produto_maquina.c.id_maquina)
        .where(Maquina.ativo.is_(True))
    )


def _candidato(fonte: Planejamento | SugestaoPlanejamento) -> CandidatoAprovacaoResponse:
    if isinstance(fonte, Planejamento):
        return CandidatoAprovacaoResponse(
            origem="manual", origem_id=fonte.id_planejamento, nome=fonte.nome,
            criado_em=fonte.criado_em, itens=fonte.itens,
        )

    return CandidatoAprovacaoResponse(
        origem="sugerida", origem_id=fonte.id_sugestao, nome="Sequência sugerida",
        criado_em=fonte.criado_em, itens=fonte.itens,
    )


def _resposta_aprovada(aprovacao: AprovacaoPlanejamento) -> AprovacaoPlanejamentoResponse:
    return AprovacaoPlanejamentoResponse(
        id_aprovacao=aprovacao.id_aprovacao,
        origem="manual" if aprovacao.planejamento_id is not None else "sugerida",
        origem_id=aprovacao.planejamento_id or aprovacao.sugestao_id,
        nome=aprovacao.nome,
        itens=aprovacao.itens,
        aprovado_por=aprovacao.aprovado_por,
        aprovado_em=aprovacao.aprovado_em,
    )


@router.get("/candidatos", response_model=list[CandidatoAprovacaoResponse])
def listar_candidatos(
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    ocupadas = set(db.scalars(select(ItemAprovacaoPlanejamento.ordem_id)))
    manuais = db.scalars(select(Planejamento).options(ITENS_MANUAIS))
    vinculo_elegivel = _vinculos_com_maquinas_ativas().where(
        produto_maquina.c.id_produto == OrdemProducao.produto_id,
        produto_maquina.c.id_maquina == ItemSugestaoPlanejamento.maquina_id,
    ).exists()
    tem_item_inelegivel = (
        select(ItemSugestaoPlanejamento.ordem_id)
        .join(ItemSugestaoPlanejamento.ordem)
        .where(
            ItemSugestaoPlanejamento.sugestao_id == SugestaoPlanejamento.id_sugestao,
            ~vinculo_elegivel,
        )
        .exists()
    )
    sugeridas = db.scalars(
        select(SugestaoPlanejamento).options(ITENS_SUGERIDOS).where(~tem_item_inelegivel)
    )
    candidatos = [
        _candidato(fonte)
        for fontes in (manuais, sugeridas)
        for fonte in fontes
        if fonte.itens and all(
            item.ordem.status == "PENDENTE" and item.ordem_id not in ocupadas
            for item in fonte.itens
        )
    ]
    return sorted(candidatos, key=lambda candidato: (candidato.criado_em, candidato.origem_id), reverse=True)


@router.get("", response_model=list[AprovacaoPlanejamentoResponse])
def listar_aprovacoes(
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR", "OPERADOR")),
):
    aprovadas = db.scalars(
        select(AprovacaoPlanejamento)
        .options(ITENS_APROVADOS)
        .order_by(AprovacaoPlanejamento.aprovado_em.desc(), AprovacaoPlanejamento.id_aprovacao.desc())
    )
    return [_resposta_aprovada(aprovacao) for aprovacao in aprovadas]


@router.post(
    "",
    response_model=AprovacaoPlanejamentoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={200: {"description": "Aprovação existente da mesma sequência"}},
)
def aprovar_planejamento(
    response: Response,
    dados: AprovacaoPlanejamentoCreate | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    if dados is None or dados.origem is None or dados.origem_id is None:
        raise HTTPException(404, SEM_PLANEJAMENTO)

    fonte: Planejamento | SugestaoPlanejamento | None
    if dados.origem == "manual":
        fonte = db.get(Planejamento, dados.origem_id, options=[ITENS_MANUAIS], with_for_update=True)
        campo_origem = AprovacaoPlanejamento.planejamento_id
    else:
        fonte = db.get(SugestaoPlanejamento, dados.origem_id, options=[ITENS_SUGERIDOS], with_for_update=True)
        campo_origem = AprovacaoPlanejamento.sugestao_id

    if fonte is None or not fonte.itens:
        raise HTTPException(404, SEM_PLANEJAMENTO)

    existente = db.scalar(
        select(AprovacaoPlanejamento).options(ITENS_APROVADOS).where(campo_origem == dados.origem_id)
    )
    if existente is not None:
        response.status_code = status.HTTP_200_OK
        return _resposta_aprovada(existente)

    ordens_ids = [item.ordem_id for item in fonte.itens]
    if dados.ordens_ids is not None and dados.ordens_ids != ordens_ids:
        raise HTTPException(409, "A sequência mudou. Atualize a lista antes de aprovar.")

    # Bloqueia as ordens na mesma ordem em todas as aprovações concorrentes.
    estados = db.scalars(
        select(OrdemProducao.status)
        .where(OrdemProducao.id_ordem.in_(ordens_ids))
        .order_by(OrdemProducao.id_ordem)
        .with_for_update()
    ).all()
    if any(estado != "PENDENTE" for estado in estados):
        raise HTTPException(409, "Somente ordens pendentes podem ser aprovadas.")

    ordem_aprovada = db.scalar(
        select(ItemAprovacaoPlanejamento.ordem_id)
        .where(ItemAprovacaoPlanejamento.ordem_id.in_(ordens_ids))
        .limit(1)
    )
    if ordem_aprovada is not None:
        raise HTTPException(409, ORDENS_JA_APROVADAS)

    if isinstance(fonte, SugestaoPlanejamento):
        vinculos = (
            _vinculos_com_maquinas_ativas()
            .join(OrdemProducao, OrdemProducao.produto_id == produto_maquina.c.id_produto)
            .join(ItemSugestaoPlanejamento, and_(
                ItemSugestaoPlanejamento.ordem_id == OrdemProducao.id_ordem,
                ItemSugestaoPlanejamento.maquina_id == produto_maquina.c.id_maquina,
            ))
            .where(ItemSugestaoPlanejamento.sugestao_id == fonte.id_sugestao)
            # Mantém máquinas e compatibilidades válidas até o commit da aprovação.
            .with_for_update(read=True, of=[Maquina, produto_maquina])
        )
        if len(db.scalars(vinculos).all()) != len(fonte.itens):
            raise HTTPException(409, SUGESTAO_INDISPONIVEL)

    aprovacao = AprovacaoPlanejamento(
        planejamento_id=fonte.id_planejamento if isinstance(fonte, Planejamento) else None,
        sugestao_id=fonte.id_sugestao if isinstance(fonte, SugestaoPlanejamento) else None,
        nome=fonte.nome if isinstance(fonte, Planejamento) else "Sequência sugerida",
        aprovado_por=usuario.id_usuario,
        itens=[
            ItemAprovacaoPlanejamento(
                ordem=item.ordem,
                maquina=item.maquina if isinstance(item, ItemSugestaoPlanejamento) else None,
                posicao=item.posicao,
            )
            for item in fonte.itens
        ],
    )
    db.add(aprovacao)
    try:
        db.flush()
        resultado = _resposta_aprovada(aprovacao)
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Não foi possível registrar a aprovação do planejamento.") from erro

    return resultado
