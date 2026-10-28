"""Cria a tabela de famílias de produtos para a US05."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c6f7b921ad03"
down_revision: Union[str, Sequence[str], None] = "4ba7b334799a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "families",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("TRUE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.BigInteger(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_families"),
        sa.UniqueConstraint("code", name="uq_families_code"),
        sa.CheckConstraint(
            "code = upper(trim(code)) AND length(code) > 0",
            name="ck_families_code_normalized",
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_families_name_not_empty",
        ),
        sa.CheckConstraint("version >= 1", name="ck_families_version_positive"),
    )


def downgrade() -> None:
    op.drop_table("families")
