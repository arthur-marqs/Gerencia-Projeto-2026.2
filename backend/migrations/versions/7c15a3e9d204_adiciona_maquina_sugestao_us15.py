"""Adiciona máquina aos itens da sugestão de planejamento da US15."""

from alembic import op
import sqlalchemy as sa


revision = "7c15a3e9d204"
down_revision = "13e41f6d48c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "itens_sugestao_planejamento",
        sa.Column("maquina_id", sa.UUID(), nullable=True),
    )

    op.create_foreign_key(
        "fk_item_sugestao_maquina",
        "itens_sugestao_planejamento",
        "maquinas",
        ["maquina_id"],
        ["id_maquina"],
    )

    op.create_index(
        "ix_itens_sugestao_planejamento_maquina_id",
        "itens_sugestao_planejamento",
        ["maquina_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_itens_sugestao_planejamento_maquina_id",
        table_name="itens_sugestao_planejamento",
    )

    op.drop_constraint(
        "fk_item_sugestao_maquina",
        "itens_sugestao_planejamento",
        type_="foreignkey",
    )

    op.drop_column("itens_sugestao_planejamento", "maquina_id")
