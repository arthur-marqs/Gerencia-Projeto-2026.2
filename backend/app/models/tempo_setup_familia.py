from datetime import datetime
from uuid import UUID

from sqlalchemy import (
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
from app.models.family import Family


class TempoSetupFamilia(Base):
    __tablename__ = "tempos_setup_familias"

    id_tempo_setup: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    familia_origem_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "families.id",
            name="fk_tempo_setup_familias_origem",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    familia_destino_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "families.id",
            name="fk_tempo_setup_familias_destino",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    tempo_setup_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    familia_origem: Mapped[Family] = relationship(
        foreign_keys=[familia_origem_id],
    )
    familia_destino: Mapped[Family] = relationship(
        foreign_keys=[familia_destino_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "familia_origem_id",
            "familia_destino_id",
            name="uq_tempo_setup_familias_origem_destino",
        ),
        CheckConstraint(
            "familia_origem_id <> familia_destino_id",
            name="ck_tempo_setup_familias_origem_destino_diferentes",
        ),
        CheckConstraint(
            "tempo_setup_minutos > 0",
            name="ck_tempo_setup_familias_tempo_positivo",
        ),
    )
