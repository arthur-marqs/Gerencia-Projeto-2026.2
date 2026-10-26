from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sessao(Base):
    __tablename__ = "sessoes"

    id_sessao: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    id_usuario: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "usuarios.id_usuario",
            name="fk_sessoes_usuario",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    invalidada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_sessoes_token_hash"),
        CheckConstraint(
            "token_hash ~ '^[0-9a-f]{64}$'",
            name="ck_sessoes_token_hash",
        ),
        CheckConstraint(
            "expira_em > criada_em",
            name="ck_sessoes_expiracao",
        ),
        CheckConstraint(
            "invalidada_em IS NULL OR invalidada_em >= criada_em",
            name="ck_sessoes_invalidacao",
        ),
        Index("ix_sessoes_usuario", "id_usuario"),
        Index("ix_sessoes_expiracao", "expira_em"),
    )