"""cria tabela produtos

Revision ID: 5ccce81c5c27
Revises: 4ba7b334799a
Create Date: 2026-10-27 12:39:35.158957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ccce81c5c27'
down_revision: Union[str, Sequence[str], None] = '4ba7b334799a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'produtos',
        sa.Column(
            'id_produto',
            sa.UUID(),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('unidade', sa.String(length=20), nullable=False),
        sa.Column(
            'ativo',
            sa.Boolean(),
            server_default=sa.text('TRUE'),
            nullable=False,
        ),
        sa.Column(
            'criado_em',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.CheckConstraint(
            'codigo = upper(trim(codigo)) AND length(codigo) > 0',
            name='ck_produtos_codigo',
        ),
        sa.CheckConstraint(
            'length(trim(nome)) > 0',
            name='ck_produtos_nome',
        ),
        sa.CheckConstraint(
            'length(trim(unidade)) > 0',
            name='ck_produtos_unidade',
        ),
        sa.PrimaryKeyConstraint('id_produto'),
        sa.UniqueConstraint(
            'codigo',
            name='uq_produtos_codigo',
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('produtos')