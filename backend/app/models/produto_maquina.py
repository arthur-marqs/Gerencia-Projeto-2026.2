
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


produto_maquina = Table(
    "produto_maquina",
    Base.metadata,
    Column(
        "id_produto",
        UUID(as_uuid=True),
        ForeignKey(
            "produtos.id_produto",
            name="fk_produto_maquina_produto",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    Column(
        "id_maquina",
        UUID(as_uuid=True),
        ForeignKey(
            "maquinas.id_maquina",
            name="fk_produto_maquina_maquina",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    PrimaryKeyConstraint(
        "id_produto",
        "id_maquina",
        name="pk_produto_maquina",
    ),
    Index("ix_produto_maquina_maquina", "id_maquina"),
)
