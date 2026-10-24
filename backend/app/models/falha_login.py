from datetime import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String, func, text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FalhaLogin(Base):
    __tablename__ = "falhas_login"

    id_falha: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email_tentado: Mapped[str] = mapped_column(String(254), nullable=False)
    ip_origem: Mapped[str] = mapped_column(INET, nullable=False)
    ocorrida_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["email_tentado", "ip_origem"],
            [
                "controle_tentativas_login.email_tentado",
                "controle_tentativas_login.ip_origem",
            ],
            name="fk_falhas_login_controle",
            ondelete="CASCADE",
        ),
    Index(
        "ix_falhas_login_combinacao_data",
        "email_tentado",
        "ip_origem",
        "ocorrida_em",
    ),
    )