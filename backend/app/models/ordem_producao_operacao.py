from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ordem_producao import OrdemProducao


class OrdemProducaoOperacao(Base):
    __tablename__ = "ordens_producao_operacoes"

    id_operacao: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id_usuario", name="fk_ordens_producao_operacoes_usuario_id"),
        nullable=False,
    )
    chave: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    hash_conteudo: Mapped[str] = mapped_column(String(64), nullable=False)
    criado_em: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    ordem: Mapped["OrdemProducao | None"] = relationship(
        back_populates="operacao",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "chave",
            name="uq_ordens_producao_operacoes_usuario_chave",
        ),
    )
