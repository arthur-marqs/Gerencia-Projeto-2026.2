"""Permite setup maior quando o sequenciamento considera a urgência."""

from alembic import op


revision = "6b14a2e9c703"
down_revision = "13e41f6d48c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_sugestao_planejamento_tempos",
        "sugestoes_planejamento",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sugestao_planejamento_tempos",
        "sugestoes_planejamento",
        "tempo_setup_original_minutos >= 0 AND tempo_setup_total_minutos >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_sugestao_planejamento_tempos",
        "sugestoes_planejamento",
        type_="check",
    )
    op.create_check_constraint(
        "ck_sugestao_planejamento_tempos",
        "sugestoes_planejamento",
        "tempo_setup_total_minutos >= 0 "
        "AND tempo_setup_total_minutos <= tempo_setup_original_minutos",
    )
