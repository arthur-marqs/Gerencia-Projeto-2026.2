from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

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
from app.services.distribuicao_maquinas import (
    distribuir_ordens,
    redistribuir_com_setups_cadastrados,
)
from app.services.sequenciamento import DadosSequenciamento
from app.services.sequenciamento_maquinas import sugerir_sequencia_por_maquina

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
            .options(
                joinedload(OrdemProducao.produto).joinedload(Produto.family),
                joinedload(OrdemProducao.produto).selectinload(
                    Produto.maquinas_compativeis
                ),
            )
            .where(OrdemProducao.id_ordem.in_(dados.ordens_ids))
        )
    }
    if len(ordens) != len(dados.ordens_ids):
        raise HTTPException(404, "Uma ou mais ordens de produção não foram encontradas.")
    if any(ordem.status != "PENDENTE" for ordem in ordens.values()):
        raise HTTPException(422, "Somente ordens pendentes podem ser planejadas.")


    familias_por_ordem: dict[UUID, UUID] = {}
    codigos_familias: dict[UUID, str] = {}
    maquinas_por_ordem: dict[UUID, dict[UUID, str]] = {}
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
            familia_id = UUID(str(produto.family.id))
            familias_por_ordem[ordem_id] = familia_id
            codigos_familias[familia_id] = produto.family.code

        maquinas = {
            UUID(str(maquina.id_maquina)): maquina.codigo
            for maquina in produto.maquinas_compativeis
            if maquina.ativo
        }

        if not maquinas:
            pendencias.append(
                f"A ordem {ordem.codigo} usa o produto {produto.codigo} "
                f"({produto.nome}), que não possui máquina compatível ativa."
            )
        else:
            maquinas_por_ordem[ordem_id] = maquinas

    distribuicao = distribuir_ordens(maquinas_por_ordem)

    familias_por_maquina: dict[UUID, list[UUID]] = {}

    for ordem_id, maquina_id in distribuicao.items():
        if ordem_id not in familias_por_ordem:
            continue

        familia_id = familias_por_ordem[ordem_id]
        familias = familias_por_maquina.setdefault(maquina_id, [])

        if familia_id not in familias:
            familias.append(familia_id)

    pares_necessarios = dict.fromkeys(
        (origem, destino)
        for familias in familias_por_maquina.values()
        for origem in familias
        for destino in familias
        if origem != destino
    )

    tempos: dict[tuple[UUID, UUID], int] = {}

    if pares_necessarios:
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

        setups_ausentes = [par for par in pares_necessarios if par not in tempos]
        if setups_ausentes and not pendencias:
            alternativa = redistribuir_com_setups_cadastrados(
                maquinas_por_ordem, familias_por_ordem, tempos,
            )
            if alternativa is not None:
                distribuicao = alternativa
                setups_ausentes = []

        pendencias.extend(
            f"Tempo de setup de {codigos_familias[origem]} "
            f"→ {codigos_familias[destino]} sem cadastro."
            for origem, destino in setups_ausentes
        )

    dados_por_ordem: dict[UUID, DadosSequenciamento] | None = None

    considera_urgencia = any(
        ordem.prazo is not None or ordem.prioridade is not None
        for ordem in ordens.values()
    )

    if considera_urgencia:
        dados_por_ordem = {}

        for ordem_id in dados.ordens_ids:
            ordem = ordens[ordem_id]

            prazo = ordem.prazo
            prioridade = ordem.prioridade
            duracao = ordem.duracao_estimada_minutos

            if prazo is None or prioridade is None or duracao is None:
                campos_ausentes = []

                if prazo is None:
                    campos_ausentes.append("prazo")

                if prioridade is None:
                    campos_ausentes.append("prioridade")

                if duracao is None:
                    campos_ausentes.append("duração estimada")

                pendencias.append(
                    f"A ordem {ordem.codigo} está sem: "
                    f"{', '.join(campos_ausentes)}."
                )
                continue

            dados_por_ordem[ordem_id] = DadosSequenciamento(
                prazo=prazo,
                prioridade=prioridade,
                duracao_estimada_minutos=duracao,
            )

    if pendencias:
        raise HTTPException(422, "\n".join(pendencias))

    sequencia, setups, total_original = sugerir_sequencia_por_maquina(
        familias_por_ordem,
        distribuicao,
        tempos,
        dados_por_ordem=dados_por_ordem,
        inicio=datetime.now(ZoneInfo("America/Recife")),
    )

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
                maquina_id=distribuicao[ordem_id],
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
