"""une migracoes de produtos e familias

Revision ID: 3e789560b2f5
Revises: 5ccce81c5c27, c6f7b921ad03
Create Date: 2026-10-28 01:05:20.904052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e789560b2f5'
down_revision: Union[str, Sequence[str], None] = ('5ccce81c5c27', 'c6f7b921ad03')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
