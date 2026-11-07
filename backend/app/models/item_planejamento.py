
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.planejamento import Planejamento
    from app.models.ordem_producao import OrdemProducao


class ItemPlanejamento(Base):
    __tablename__ = "itens_planejamento"

    id_item: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    planejamento_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "planejamentos.id_planejamento",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    ordem_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ordens_producao.id_ordem"),
        nullable=False,
    )

    posicao: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    planejamento: Mapped["Planejamento"] = relationship(
        back_populates="itens",
    )

    ordem: Mapped["OrdemProducao"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "planejamento_id",
            "ordem_id",
            name="uq_item_planejamento_ordem",
        ),
        UniqueConstraint(
            "planejamento_id",
            "posicao",
            name="uq_item_planejamento_posicao",
        ),
        CheckConstraint(
            "posicao > 0",
            name="ck_item_planejamento_posicao_positiva",
        ),
        UniqueConstraint(
            "ordem_id",
            name="uq_item_planejamento_ordem_global",
        ),
    )
