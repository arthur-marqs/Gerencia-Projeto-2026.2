from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ControleTentativasLogin(Base):
    __tablename__ = "controle_tentativas_login"

    email_tentado: Mapped[str] = mapped_column(String(254), nullable=False)
    ip_origem: Mapped[str] = mapped_column(INET, nullable=False)
    bloqueado_ate: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "email_tentado",
            "ip_origem",
            name="pk_controle_tentativas_login",
        ),
        CheckConstraint(
            "email_tentado = lower(trim(email_tentado)) "
            "AND length(email_tentado) > 0",
            name="ck_controle_email_normalizado",
        ),
    )