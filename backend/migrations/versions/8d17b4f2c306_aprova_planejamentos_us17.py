"""Registra sequências aprovadas para execução (US17)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "8d17b4f2c306"
down_revision = "b872837156bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "aprovacoes_planejamento",
        sa.Column("id_aprovacao", uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("planejamento_id", uuid, sa.ForeignKey("planejamentos.id_planejamento")),
        sa.Column("sugestao_id", uuid, sa.ForeignKey("sugestoes_planejamento.id_sugestao")),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("aprovado_por", uuid, sa.ForeignKey("usuarios.id_usuario"), nullable=False),
        sa.Column("aprovado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "(planejamento_id IS NOT NULL) <> (sugestao_id IS NOT NULL)",
            name="ck_aprovacao_planejamento_origem",
        ),
        sa.UniqueConstraint("planejamento_id", name="uq_aprovacao_planejamento_manual"),
        sa.UniqueConstraint("sugestao_id", name="uq_aprovacao_planejamento_sugerida"),
    )
    op.create_table(
        "itens_aprovacao_planejamento",
        sa.Column("ordem_id", uuid, sa.ForeignKey("ordens_producao.id_ordem"), primary_key=True),
        sa.Column(
            "aprovacao_id", uuid,
            sa.ForeignKey("aprovacoes_planejamento.id_aprovacao", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("maquina_id", uuid, sa.ForeignKey("maquinas.id_maquina")),
        sa.Column("posicao", sa.Integer(), nullable=False),
        sa.UniqueConstraint("aprovacao_id", "posicao", name="uq_item_aprovacao_posicao"),
        sa.CheckConstraint("posicao > 0", name="ck_item_aprovacao_posicao_positiva"),
    )


def downgrade() -> None:
    op.drop_table("itens_aprovacao_planejamento")
    op.drop_table("aprovacoes_planejamento")
