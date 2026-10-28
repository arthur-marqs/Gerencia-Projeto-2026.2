from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    text,
)
from uuid import UUID

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.family import Family


class Produto(Base):
    __tablename__ = "produtos"

    id_produto: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)

    family_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "families.id",
            name="fk_produtos_family_id",
        ),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )
    criado_em: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    family: Mapped["Family | None"] = relationship(
        back_populates="produtos",
    )

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_produtos_codigo"),
        CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_produtos_codigo",
        ),
        CheckConstraint(
            "length(trim(nome)) > 0",
            name="ck_produtos_nome",
        ),
        CheckConstraint(
            "length(trim(unidade)) > 0",
            name="ck_produtos_unidade",
        ),
    )
