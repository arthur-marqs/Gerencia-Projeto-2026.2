from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.produto import Produto

class Family(Base):
    __tablename__ = "families"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        server_default=text("1"),
    )
    produtos: Mapped[list["Produto"]] = relationship(
        back_populates="family",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_families_code"),
        CheckConstraint(
            "code = upper(trim(code)) AND length(code) > 0",
            name="ck_families_code_normalized",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_families_name_not_empty",
        ),
        CheckConstraint("version >= 1", name="ck_families_version_positive"),
    )
