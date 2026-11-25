"""unifica migrations US14 e US15

Revision ID: b872837156bd
Revises: 6b14a2e9c703, 7c15a3e9d204
Create Date: 2026-11-25 15:40:00.716414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b872837156bd'
down_revision: Union[str, Sequence[str], None] = ('6b14a2e9c703', '7c15a3e9d204')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
