from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.produto import Produto
    from app.models.ordem_producao_operacao import OrdemProducaoOperacao


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
    operacao_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    criado_em: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    produto: Mapped["Produto"] = relationship()
    operacao: Mapped["OrdemProducaoOperacao | None"] = relationship(
        back_populates="ordem",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_ordens_producao_codigo"),
        UniqueConstraint("operacao_id", name="uq_ordens_producao_operacao_id"),
        ForeignKeyConstraint(
            ["operacao_id"],
            ["ordens_producao_operacoes.id_operacao"],
            name="fk_ordens_producao_operacao_id",
        ),
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
    )
