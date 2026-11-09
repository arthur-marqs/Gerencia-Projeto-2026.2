"""Cria a tabela de tempos de setup entre famílias (US10)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e1a7c9d4b602"
down_revision: Union[str, Sequence[str], None] = "d4e8f6a2c901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tempos_setup_familias",
        sa.Column(
            "id_tempo_setup",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("familia_origem_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("familia_destino_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tempo_setup_minutos", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_tempo_setup", name="pk_tempos_setup_familias"),
        sa.ForeignKeyConstraint(
            ["familia_origem_id"],
            ["families.id"],
            name="fk_tempo_setup_familias_origem",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["familia_destino_id"],
            ["families.id"],
            name="fk_tempo_setup_familias_destino",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "familia_origem_id",
            "familia_destino_id",
            name="uq_tempo_setup_familias_origem_destino",
        ),
        sa.CheckConstraint(
            "familia_origem_id <> familia_destino_id",
            name="ck_tempo_setup_familias_origem_destino_diferentes",
        ),
        sa.CheckConstraint(
            "tempo_setup_minutos > 0",
            name="ck_tempo_setup_familias_tempo_positivo",
        ),
    )


def downgrade() -> None:
    op.drop_table("tempos_setup_familias")
