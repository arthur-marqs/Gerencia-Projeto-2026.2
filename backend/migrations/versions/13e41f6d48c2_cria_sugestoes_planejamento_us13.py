"""Cria as tabelas de sugestões de planejamento da US13."""

from alembic import op
import sqlalchemy as sa


revision = "13e41f6d48c2"
down_revision = "f032ad660001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sugestoes_planejamento",
        sa.Column("id_sugestao", sa.UUID(), server_default=sa.text("gen_random_uuid()")),
        sa.Column("criado_por", sa.UUID(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column("tempo_setup_original_minutos", sa.BigInteger(), nullable=False),
        sa.Column("tempo_setup_total_minutos", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id_sugestao"),
        sa.ForeignKeyConstraint(["criado_por"], ["usuarios.id_usuario"]),
        sa.CheckConstraint(
            "tempo_setup_total_minutos >= 0 "
            "AND tempo_setup_total_minutos <= tempo_setup_original_minutos",
            name="ck_sugestao_planejamento_tempos",
        ),
    )
    op.create_table(
        "itens_sugestao_planejamento",
        sa.Column("sugestao_id", sa.UUID()),
        sa.Column("ordem_id", sa.UUID()),
        sa.Column("posicao", sa.Integer(), nullable=False),
        sa.Column("posicao_original", sa.Integer(), nullable=False),
        sa.Column("setup_minutos", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("sugestao_id", "ordem_id"),
        sa.ForeignKeyConstraint(["sugestao_id"], ["sugestoes_planejamento.id_sugestao"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordem_id"], ["ordens_producao.id_ordem"]),
        sa.UniqueConstraint("sugestao_id", "posicao", name="uq_item_sugestao_posicao"),
        sa.UniqueConstraint("sugestao_id", "posicao_original", name="uq_item_sugestao_posicao_original"),
        sa.CheckConstraint("posicao > 0 AND posicao_original > 0", name="ck_item_sugestao_posicoes"),
        sa.CheckConstraint(
            "setup_minutos >= 0 AND (posicao <> 1 OR setup_minutos = 0)",
            name="ck_item_sugestao_setup",
        ),
    )
    op.create_index("ix_itens_sugestao_planejamento_ordem_id", "itens_sugestao_planejamento", ["ordem_id"])


def downgrade() -> None:
    op.drop_table("itens_sugestao_planejamento")
    op.drop_table("sugestoes_planejamento")
