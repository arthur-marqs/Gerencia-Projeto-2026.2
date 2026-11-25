from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SugestaoPlanejamento(Base):
    __tablename__ = "sugestoes_planejamento"

    id_sugestao: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    criado_por: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id_usuario"))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    tempo_setup_original_minutos: Mapped[int] = mapped_column(BigInteger)
    tempo_setup_total_minutos: Mapped[int] = mapped_column(BigInteger)
    itens: Mapped[list["ItemSugestaoPlanejamento"]] = relationship(
        cascade="all, delete-orphan", order_by="ItemSugestaoPlanejamento.posicao"
    )

    __table_args__ = (
        CheckConstraint(
            "tempo_setup_original_minutos >= 0 "
            "AND tempo_setup_total_minutos >= 0",
            name="ck_sugestao_planejamento_tempos",
        ),
    )


class ItemSugestaoPlanejamento(Base):
    __tablename__ = "itens_sugestao_planejamento"

    sugestao_id: Mapped[UUID] = mapped_column(
        ForeignKey("sugestoes_planejamento.id_sugestao", ondelete="CASCADE"),
        primary_key=True,
    )
    ordem_id: Mapped[UUID] = mapped_column(
        ForeignKey("ordens_producao.id_ordem"), primary_key=True, index=True
    )
    maquina_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "maquinas.id_maquina",
            name="fk_item_sugestao_maquina",
        ),
        nullable=True,
        index=True,
    )
    posicao: Mapped[int] = mapped_column(Integer)
    posicao_original: Mapped[int] = mapped_column(Integer)
    setup_minutos: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("sugestao_id", "posicao", name="uq_item_sugestao_posicao"),
        UniqueConstraint(
            "sugestao_id", "posicao_original", name="uq_item_sugestao_posicao_original"
        ),
        CheckConstraint(
            "posicao > 0 AND posicao_original > 0", name="ck_item_sugestao_posicoes"
        ),
        CheckConstraint(
            "setup_minutos >= 0 AND (posicao <> 1 OR setup_minutos = 0)",
            name="ck_item_sugestao_setup",
        ),
    )
