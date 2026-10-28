"""Merge machine and family migration branches.

Revision ID: 6ddbcb3397c4
Revises: 72269261cc65, 7a2c9f1d4e6b
Create Date: 2026-10-28 18:07:28.191051

"""
from typing import Sequence, Union

revision: str = '6ddbcb3397c4'
down_revision: Union[str, Sequence[str], None] = ('72269261cc65', '7a2c9f1d4e6b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
