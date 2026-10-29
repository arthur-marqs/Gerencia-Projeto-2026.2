"""adiciona prazo e prioridade às ordens de produção

Revision ID: b3f84d2e90a1
Revises: a7c1f2d9e430
Create Date: 2026-10-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3f84d2e90a1"
down_revision: Union[str, Sequence[str], None] = "a7c1f2d9e430"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ordens_producao",
        sa.Column("prazo", sa.Date(), nullable=True),
    )
    op.add_column(
        "ordens_producao",
        sa.Column("prioridade", sa.String(length=10), nullable=True),
    )
    op.create_check_constraint(
        "ck_ordens_producao_prioridade",
        "ordens_producao",
        "prioridade IS NULL OR prioridade IN ('Baixa', 'Média', 'Alta')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ordens_producao_prioridade",
        "ordens_producao",
        type_="check",
    )
    op.drop_column("ordens_producao", "prioridade")
    op.drop_column("ordens_producao", "prazo")
