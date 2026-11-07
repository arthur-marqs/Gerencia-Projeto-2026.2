"""adiciona duração estimada às ordens de produção (US09)

Revision ID: d4e8f6a2c901
Revises: fc02da88af8f
Create Date: 2026-10-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e8f6a2c901"
down_revision: Union[str, Sequence[str], None] = "fc02da88af8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ordens_producao",
        sa.Column("duracao_estimada_minutos", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_ordens_producao_duracao_estimada_positiva",
        "ordens_producao",
        "duracao_estimada_minutos IS NULL OR duracao_estimada_minutos > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ordens_producao_duracao_estimada_positiva",
        "ordens_producao",
        type_="check",
    )
    op.drop_column("ordens_producao", "duracao_estimada_minutos")
