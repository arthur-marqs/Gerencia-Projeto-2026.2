from collections.abc import Generator
from datetime import datetime, timezone
from hashlib import sha256

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.sessao import Sessao
from app.models.usuario import Usuario
from app.models.perfil import Perfil
from app.models.usuario_perfil import usuario_perfil


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str | None = Cookie(default=None, alias="setupflow_session"),
    db: Session = Depends(get_db),
) -> Usuario:
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada.",
        )

    token_hash = sha256(token.encode("utf-8")).hexdigest()
    agora = datetime.now(timezone.utc)

    usuario = db.scalar(
        select(Usuario)
        .join(Sessao, Sessao.id_usuario == Usuario.id_usuario)
        .where(
            Sessao.token_hash == token_hash,
            Sessao.invalidada_em.is_(None),
            Sessao.expira_em > agora,
            Usuario.ativo.is_(True),
        )
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada.",
        )

    return usuario


def require_profiles(*perfis_permitidos: str):
    def verificar_perfil(
        usuario: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        perfis_usuario = set(
            db.scalars(
                select(Perfil.codigo)
                .join(
                    usuario_perfil,
                    Perfil.id_perfil == usuario_perfil.c.id_perfil,
                )
                .where(
                    usuario_perfil.c.id_usuario == usuario.id_usuario
                )
            ).all()
        )

        if not perfis_usuario.intersection(perfis_permitidos):
            raise HTTPException(
                status_code=403,
                detail="Acesso não autorizado para este perfil.",
            )

        return usuario

    return verificar_perfil
