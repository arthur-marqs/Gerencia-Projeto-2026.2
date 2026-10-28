"""adiciona familia aos produtos

Revision ID: 72269261cc65
Revises: 3e789560b2f5
Create Date: 2026-10-28 14:18:45.932633

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "72269261cc65"
down_revision: Union[str, Sequence[str], None] = "3e789560b2f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "produtos",
        sa.Column(
            "family_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_produtos_family_id",
        "produtos",
        "families",
        ["family_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_produtos_family_id",
        "produtos",
        type_="foreignkey",
    )

    op.drop_column(
        "produtos",
        "family_id",
    )
