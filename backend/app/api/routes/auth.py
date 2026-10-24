from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_session_token, verify_password
from app.models.perfil import Perfil
from app.models.sessao import Sessao
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil
from app.schemas.auth import LoginRequest


router = APIRouter()


@router.post("/login")
def login(
    dados: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    usuario = db.scalar(
        select(Usuario).where(Usuario.email == dados.email)
    )

    if (
        usuario is None
        or not usuario.ativo
        or not verify_password(dados.password, usuario.senha_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    agora = datetime.now(timezone.utc)
    expira_em = agora + timedelta(hours=settings.session_ttl_hours)
    token, token_hash = create_session_token()

    db.add(
        Sessao(
            id_usuario=usuario.id_usuario,
            token_hash=token_hash,
            expira_em=expira_em,
        )
    )
    db.commit()

    response.set_cookie(
        key="setupflow_session",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_ttl_hours * 60 * 60,
        path="/",
    )

    perfis = db.scalars(
        select(Perfil.codigo)
        .join(
            usuario_perfil,
            Perfil.id_perfil == usuario_perfil.c.id_perfil,
        )
        .where(usuario_perfil.c.id_usuario == usuario.id_usuario)
    ).all()

    return {
        "mensagem": "Login realizado.",
        "usuario": {
            "id": str(usuario.id_usuario),
            "nome": usuario.nome,
            "email": usuario.email,
            "perfis": perfis,
        },
    }


@router.get("/me")
def get_current_user(
    token: str | None = Cookie(default=None, alias="setupflow_session"),
    db: Session = Depends(get_db),
):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada.",
        )

    token_hash = sha256(token.encode("utf-8")).hexdigest()
    agora = datetime.now(timezone.utc)

    consulta = (
        select(Usuario)
        .join(Sessao, Sessao.id_usuario == Usuario.id_usuario)
        .where(
            Sessao.token_hash == token_hash,
            Sessao.invalidada_em.is_(None),
            Sessao.expira_em > agora,
            Usuario.ativo.is_(True),
        )
    )

    usuario = db.scalar(consulta)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada.",
        )

    perfis = db.scalars(
        select(Perfil.codigo)
        .join(usuario_perfil, Perfil.id_perfil == usuario_perfil.c.id_perfil)
        .where(usuario_perfil.c.id_usuario == usuario.id_usuario)
    ).all()

    return {
        "usuario": {
            "id": str(usuario.id_usuario),
            "nome": usuario.nome,
            "email": usuario.email,
            "perfis": perfis,
        }
    }

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
    token: str | None = Cookie(default=None, alias="setupflow_session"),
    db: Session = Depends(get_db),
):
    if token is not None:
        token_hash = sha256(token.encode("utf-8")).hexdigest()

        sessao = db.scalar(
            select(Sessao).where(Sessao.token_hash == token_hash)
        )

        if sessao is not None and sessao.invalidada_em is None:
            sessao.invalidada_em = datetime.now(timezone.utc)
            db.commit()

    response.delete_cookie(
        key="setupflow_session",
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )