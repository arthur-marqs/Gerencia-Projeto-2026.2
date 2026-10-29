"""cria tabela ordens_producao para a US07

Revision ID: a7c1f2d9e430
Revises: 6ddbcb3397c4
Create Date: 2026-10-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c1f2d9e430"
down_revision: Union[str, Sequence[str], None] = "6ddbcb3397c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ordens_producao",
        sa.Column(
            "id_ordem",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("produto_id", sa.UUID(), nullable=False),
        sa.Column("quantidade", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDENTE'"),
            nullable=False,
        ),
        sa.Column("criado_por", sa.UUID(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "codigo = upper(trim(codigo)) AND length(codigo) > 0",
            name="ck_ordens_producao_codigo",
        ),
        sa.CheckConstraint(
            "quantidade > 0",
            name="ck_ordens_producao_quantidade_positiva",
        ),
        sa.CheckConstraint(
            "length(trim(status)) > 0",
            name="ck_ordens_producao_status",
        ),
        sa.ForeignKeyConstraint(
            ["produto_id"],
            ["produtos.id_produto"],
            name="fk_ordens_producao_produto_id",
        ),
        sa.ForeignKeyConstraint(
            ["criado_por"],
            ["usuarios.id_usuario"],
            name="fk_ordens_producao_criado_por",
        ),
        sa.PrimaryKeyConstraint("id_ordem"),
        sa.UniqueConstraint("codigo", name="uq_ordens_producao_codigo"),
    )


def downgrade() -> None:
    op.drop_table("ordens_producao")
