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
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
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

    __table_args__ = (
        UniqueConstraint("email", name="uq_usuarios_email"),
        CheckConstraint(
            "length(trim(nome)) > 0",
            name="ck_usuarios_nome",
        ),
        CheckConstraint(
            "email = lower(trim(email)) AND length(email) > 0",
            name="ck_usuarios_email_normalizado",
        ),
        CheckConstraint(
            "length(trim(senha_hash)) > 0",
            name="ck_usuarios_senha_hash",
        ),
    )