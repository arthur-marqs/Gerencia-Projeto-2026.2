from decimal import Decimal
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.produto import Produto


class OrdemProducao(Base):
    __tablename__ = "ordens_producao"

    id_ordem: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    produto_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("produtos.id_produto", name="fk_ordens_producao_produto_id"),
        nullable=False,
    )
    quantidade: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'PENDENTE'")
    )
    criado_por: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id_usuario", name="fk_ordens_producao_criado_por"),
        nullable=False,
    )
    criado_em: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    prazo: Mapped[date | None] = mapped_column(nullable=True)
    prioridade: Mapped[str | None] = mapped_column(String(10), nullable=True)

    produto: Mapped["Produto"] = relationship()

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_ordens_producao_codigo"),
        CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_ordens_producao_codigo",
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_ordens_producao_quantidade_positiva",
        ),
        CheckConstraint(
            "length(trim(status)) > 0",
            name="ck_ordens_producao_status",
        ),
        CheckConstraint(
            "prioridade IS NULL OR prioridade IN ('Baixa', 'Média', 'Alta')",
            name="ck_ordens_producao_prioridade",
        ),
    )
