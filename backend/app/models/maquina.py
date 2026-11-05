from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.produto import Produto

class Maquina(Base):
    __tablename__ = "maquinas"

    id_maquina: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    produtos_compativeis: Mapped[list["Produto"]] = relationship(
        secondary="produto_maquina",
        back_populates="maquinas_compativeis",
    )

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_maquinas_codigo"),
        CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_maquinas_codigo",
        ),
        CheckConstraint(
            "length(trim(nome)) > 0",
            name="ck_maquinas_nome",
        ),
    )
