from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import get_db, require_profiles
from app.models.item_planejamento import ItemPlanejamento
from app.models.ordem_producao import OrdemProducao
from app.models.planejamento import Planejamento
from app.models.produto import Produto
from app.models.sugestao_planejamento import ItemSugestaoPlanejamento, SugestaoPlanejamento
from app.models.tempo_setup_familia import TempoSetupFamilia
from app.models.usuario import Usuario
from app.schemas.planejamento import SugestaoPlanejamentoCreate, SugestaoPlanejamentoResponse
from app.services.sequenciamento import sugerir_sequencia


router = APIRouter()


@router.post(
    "/sugestoes",
    response_model=SugestaoPlanejamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def gerar_sugestao(
    dados: SugestaoPlanejamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    if not dados.ordens_ids:
        raise HTTPException(422, "Selecione pelo menos uma ordem para gerar a sugestão.")
    if len(dados.ordens_ids) != len(set(dados.ordens_ids)):
        raise HTTPException(422, "Cada ordem pode ser selecionada apenas uma vez.")

    ordens = {
        ordem.id_ordem: ordem
        for ordem in db.scalars(
            select(OrdemProducao)
            .options(joinedload(OrdemProducao.produto).joinedload(Produto.family))
            .where(OrdemProducao.id_ordem.in_(dados.ordens_ids))
        )
    }
    if len(ordens) != len(dados.ordens_ids):
        raise HTTPException(404, "Uma ou mais ordens de produção não foram encontradas.")
    if any(ordem.status != "PENDENTE" for ordem in ordens.values()):
        raise HTTPException(422, "Somente ordens pendentes podem ser planejadas.")

    familias_por_ordem: dict[UUID, UUID] = {}
    codigos_familias: dict[UUID, str] = {}
    pendencias = []
    for ordem_id in dados.ordens_ids:
        ordem = ordens[ordem_id]
        produto = ordem.produto
        if produto.family is None:
            pendencias.append(
                f"A ordem {ordem.codigo} usa o produto {produto.codigo} "
                f"({produto.nome}), que está sem família associada."
            )
        else:
            familias_por_ordem[ordem_id] = produto.family.id
            codigos_familias[produto.family.id] = produto.family.code

    tempos: dict[tuple[UUID, UUID], int] = {}
    if len(codigos_familias) > 1:
        familias = list(codigos_familias)
        tempos = {
            (origem, destino): minutos
            for origem, destino, minutos in db.execute(
                select(
                    TempoSetupFamilia.familia_origem_id,
                    TempoSetupFamilia.familia_destino_id,
                    TempoSetupFamilia.tempo_setup_minutos,
                ).where(
                    TempoSetupFamilia.familia_origem_id.in_(familias),
                    TempoSetupFamilia.familia_destino_id.in_(familias),
                )
            )
        }
        pendencias.extend(
            f"Tempo de setup de {codigo_origem} → {codigo_destino} sem cadastro."
            for origem, codigo_origem in codigos_familias.items()
            for destino, codigo_destino in codigos_familias.items()
            if origem != destino and (origem, destino) not in tempos
        )

    if pendencias:
        raise HTTPException(422, "\n".join(pendencias))

    sequencia, setups, total_original = sugerir_sequencia(familias_por_ordem, tempos)
    posicoes_originais = {
        ordem_id: posicao for posicao, ordem_id in enumerate(dados.ordens_ids, start=1)
    }
    sugestao = SugestaoPlanejamento(
        criado_por=usuario.id_usuario,
        tempo_setup_original_minutos=total_original,
        tempo_setup_total_minutos=sum(setups),
        itens=[
            ItemSugestaoPlanejamento(
                ordem_id=ordem_id,
                posicao=posicao,
                posicao_original=posicoes_originais[ordem_id],
                setup_minutos=setup,
            )
            for posicao, (ordem_id, setup) in enumerate(zip(sequencia, setups, strict=True), start=1)
        ],
    )
    db.add(sugestao)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Não foi possível salvar a sequência sugerida.") from erro
    return sugestao


@router.get("/sugestoes/{id_sugestao}", response_model=SugestaoPlanejamentoResponse)
def consultar_sugestao(
    id_sugestao: UUID,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    sugestao = db.get(SugestaoPlanejamento, id_sugestao, options=[selectinload(SugestaoPlanejamento.itens)])
    if sugestao is None:
        raise HTTPException(404, "Sugestão não encontrada.")
    return sugestao


@router.get("/{id_planejamento}/sugestao", response_model=SugestaoPlanejamentoResponse)
def consultar_sugestao_do_planejamento(
    id_planejamento: UUID,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(require_profiles("PLANEJADOR")),
):
    ordens_ids = db.scalars(
        select(ItemPlanejamento.ordem_id).where(ItemPlanejamento.planejamento_id == id_planejamento)
    ).all()
    if not ordens_ids and db.get(Planejamento, id_planejamento) is None:
        raise HTTPException(404, "Planejamento não encontrado.")

    sugestoes_com_todas_as_ordens = (
        select(ItemSugestaoPlanejamento.sugestao_id)
        .where(ItemSugestaoPlanejamento.ordem_id.in_(ordens_ids))
        .group_by(ItemSugestaoPlanejamento.sugestao_id)
        .having(func.count() == len(ordens_ids))
    )
    sugestao = db.scalar(
        select(SugestaoPlanejamento)
        .options(selectinload(SugestaoPlanejamento.itens))
        .where(
            SugestaoPlanejamento.id_sugestao.in_(sugestoes_com_todas_as_ordens),
            ~SugestaoPlanejamento.itens.any(ItemSugestaoPlanejamento.ordem_id.not_in(ordens_ids)),
        )
        .order_by(SugestaoPlanejamento.criado_em.desc(), SugestaoPlanejamento.id_sugestao.desc())
        .limit(1)
    )
    if sugestao is None:
        raise HTTPException(404, "Nenhuma sugestão foi gerada para as ordens deste planejamento.")
    return sugestao
