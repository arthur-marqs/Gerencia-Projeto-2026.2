"""Insere perfis de acesso."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4ba7b334799a"
down_revision: Union[str, Sequence[str], None] = "8c4926160d84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    perfis = sa.table(
        "perfis",
        sa.column("codigo", sa.String(length=30)),
        sa.column("nome", sa.String(length=80)),
        sa.column("descricao", sa.Text()),
    )

    op.bulk_insert(
        perfis,
        [
            {
                "codigo": "PLANEJADOR",
                "nome": "Planejador de Produ\u00e7\u00e3o",
                "descricao": (
                    "Perfil respons\u00e1vel pelo planejamento da produ\u00e7\u00e3o."
                ),
            },
            {
                "codigo": "OPERADOR",
                "nome": "Operador",
                "descricao": "Perfil de opera\u00e7\u00e3o da produ\u00e7\u00e3o.",
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM perfis
            WHERE codigo IN ('PLANEJADOR', 'OPERADOR')
            """
        )
    )