"""adiciona idempotência ao cadastro de ordens de produção

Revision ID: c4e8a1927f30
Revises: a7c1f2d9e430
Create Date: 2026-10-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8a1927f30"
down_revision: Union[str, Sequence[str], None] = "a7c1f2d9e430"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ordens_producao_operacoes",
        sa.Column(
            "id_operacao",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("usuario_id", sa.UUID(), nullable=False),
        sa.Column("chave", sa.UUID(), nullable=False),
        sa.Column("hash_conteudo", sa.String(length=64), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id_usuario"],
            name="fk_ordens_producao_operacoes_usuario_id",
        ),
        sa.PrimaryKeyConstraint("id_operacao"),
        sa.UniqueConstraint(
            "usuario_id",
            "chave",
            name="uq_ordens_producao_operacoes_usuario_chave",
        ),
    )
    op.add_column(
        "ordens_producao",
        sa.Column("operacao_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ordens_producao_operacao_id",
        "ordens_producao",
        "ordens_producao_operacoes",
        ["operacao_id"],
        ["id_operacao"],
    )
    op.create_unique_constraint(
        "uq_ordens_producao_operacao_id",
        "ordens_producao",
        ["operacao_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_ordens_producao_operacao_id",
        "ordens_producao",
        type_="unique",
    )
    op.drop_constraint(
        "fk_ordens_producao_operacao_id",
        "ordens_producao",
        type_="foreignkey",
    )
    op.drop_column("ordens_producao", "operacao_id")
    op.drop_table("ordens_producao_operacoes")
