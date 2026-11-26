from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.maquina import Maquina
    from app.models.ordem_producao import OrdemProducao


class AprovacaoPlanejamento(Base):
    __tablename__ = "aprovacoes_planejamento"

    id_aprovacao: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    planejamento_id: Mapped[UUID | None] = mapped_column(ForeignKey("planejamentos.id_planejamento"))
    sugestao_id: Mapped[UUID | None] = mapped_column(ForeignKey("sugestoes_planejamento.id_sugestao"))
    nome: Mapped[str] = mapped_column(String(150))
    aprovado_por: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id_usuario"))
    aprovado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    itens: Mapped[list["ItemAprovacaoPlanejamento"]] = relationship(
        cascade="all, delete-orphan", order_by="ItemAprovacaoPlanejamento.posicao"
    )

    __table_args__ = (
        CheckConstraint(
            "(planejamento_id IS NOT NULL) <> (sugestao_id IS NOT NULL)",
            name="ck_aprovacao_planejamento_origem",
        ),
        UniqueConstraint("planejamento_id", name="uq_aprovacao_planejamento_manual"),
        UniqueConstraint("sugestao_id", name="uq_aprovacao_planejamento_sugerida"),
    )


class ItemAprovacaoPlanejamento(Base):
    __tablename__ = "itens_aprovacao_planejamento"

    ordem_id: Mapped[UUID] = mapped_column(ForeignKey("ordens_producao.id_ordem"), primary_key=True)
    aprovacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("aprovacoes_planejamento.id_aprovacao", ondelete="CASCADE")
    )
    maquina_id: Mapped[UUID | None] = mapped_column(ForeignKey("maquinas.id_maquina"))
    posicao: Mapped[int] = mapped_column(Integer)
    ordem: Mapped["OrdemProducao"] = relationship()
    maquina: Mapped["Maquina | None"] = relationship()

    __table_args__ = (
        UniqueConstraint("aprovacao_id", "posicao", name="uq_item_aprovacao_posicao"),
        CheckConstraint("posicao > 0", name="ck_item_aprovacao_posicao_positiva"),
    )
