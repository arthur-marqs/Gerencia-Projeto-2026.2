"""une migracoes us10 e us12

Revision ID: 9a420823b051
Revises: 7ba9a321106c, e1a7c9d4b602
Create Date: 2026-11-09 08:38:11.600074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a420823b051'
down_revision: Union[str, Sequence[str], None] = ('7ba9a321106c', 'e1a7c9d4b602')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
