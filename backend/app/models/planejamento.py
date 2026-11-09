
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.item_planejamento import ItemPlanejamento


class Planejamento(Base):
    __tablename__ = "planejamentos"

    id_planejamento: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    criado_por: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id_usuario"),
        nullable=False,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    itens: Mapped[list["ItemPlanejamento"]] = relationship(
        back_populates="planejamento",
        cascade="all, delete-orphan",
        order_by="ItemPlanejamento.posicao",
    )
