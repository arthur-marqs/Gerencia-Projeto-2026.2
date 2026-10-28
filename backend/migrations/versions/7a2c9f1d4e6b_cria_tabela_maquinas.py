"""cria tabela maquinas

Revision ID: 7a2c9f1d4e6b
Revises: 5ccce81c5c27
Create Date: 2026-10-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a2c9f1d4e6b"
down_revision: Union[str, Sequence[str], None] = "5ccce81c5c27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "maquinas",
        sa.Column(
            "id_maquina",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "ativo",
            sa.Boolean(),
            server_default=sa.text("TRUE"),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_maquinas_codigo",
        ),
        sa.CheckConstraint(
            "length(trim(nome)) > 0",
            name="ck_maquinas_nome",
        ),
        sa.PrimaryKeyConstraint("id_maquina"),
        sa.UniqueConstraint("codigo", name="uq_maquinas_codigo"),
    )


def downgrade() -> None:
    op.drop_table("maquinas")
