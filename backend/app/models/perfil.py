from sqlalchemy import CheckConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Perfil(Base):
    __tablename__ = "perfis"

    id_perfil: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    codigo: Mapped[str] = mapped_column(String(30), nullable=False)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("codigo", name="uq_perfis_codigo"),
        CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_perfis_codigo",
        ),
        CheckConstraint(
            "length(trim(nome)) > 0",
            name="ck_perfis_nome",
        ),
    )