from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


usuario_perfil = Table(
    "usuario_perfil",
    Base.metadata,
    Column(
        "id_usuario",
        UUID(as_uuid=True),
        ForeignKey(
            "usuarios.id_usuario",
            name="fk_usuario_perfil_usuario",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    Column(
        "id_perfil",
        UUID(as_uuid=True),
        ForeignKey(
            "perfis.id_perfil",
            name="fk_usuario_perfil_perfil",
            ondelete="RESTRICT",
        ),
        nullable=False,
    ),
    PrimaryKeyConstraint(
        "id_usuario",
        "id_perfil",
        name="pk_usuario_perfil",
    ),
    Index("ix_usuario_perfil_perfil", "id_perfil"),
)