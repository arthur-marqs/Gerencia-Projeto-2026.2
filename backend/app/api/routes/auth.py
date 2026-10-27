from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status, Request

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_session_token, verify_password
from app.models.perfil import Perfil
from app.models.sessao import Sessao
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil
from app.models.controle_tentativas_login import ControleTentativasLogin
from app.models.falha_login import FalhaLogin
from app.schemas.auth import LoginRequest


router = APIRouter()


@router.post("/login")
def login(
    dados: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ip_origem = request.client.host if request.client else "0.0.0.0"
    agora = datetime.now(timezone.utc)
    inicio_janela = agora - timedelta(minutes=5)

    db.execute(
        pg_insert(ControleTentativasLogin)
        .values(email_tentado=dados.email, ip_origem=ip_origem)
        .on_conflict_do_nothing(
            index_elements=[
                ControleTentativasLogin.email_tentado,
                ControleTentativasLogin.ip_origem,
            ]
        )
    )

    controle = db.scalar(
        select(ControleTentativasLogin)
        .where(
            ControleTentativasLogin.email_tentado == dados.email,
            ControleTentativasLogin.ip_origem == ip_origem,
        )
        .with_for_update()
    )

    if controle is None:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível processar o login.",
        )

    if controle.bloqueado_ate is not None and controle.bloqueado_ate > agora:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente em 15 minutos.",
        )

    usuario = db.scalar(
        select(Usuario).where(Usuario.email == dados.email)
    )

    if (
        usuario is None
        or not usuario.ativo
        or not verify_password(dados.password, usuario.senha_hash)
    ):
        db.execute(
            delete(FalhaLogin).where(
                FalhaLogin.email_tentado == dados.email,
                FalhaLogin.ip_origem == ip_origem,
                FalhaLogin.ocorrida_em < inicio_janela,
            )
        )
        db.add(
            FalhaLogin(
                email_tentado=dados.email,
                ip_origem=ip_origem,
            )
        )
        db.flush()

        total_falhas = db.scalar(
            select(func.count(FalhaLogin.id_falha)).where(
                FalhaLogin.email_tentado == dados.email,
                FalhaLogin.ip_origem == ip_origem,
                FalhaLogin.ocorrida_em >= inicio_janela,
            )
        ) or 0

        if total_falhas >= 5:
            controle.bloqueado_ate = agora + timedelta(minutes=15)

        controle.atualizado_em = agora
        db.commit()

        if total_falhas >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Tente novamente em 15 minutos.",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível entrar. Verifique suas credenciais.",
        )

    db.execute(
        delete(FalhaLogin).where(
            FalhaLogin.email_tentado == dados.email,
            FalhaLogin.ip_origem == ip_origem,
        )
    )
    controle.bloqueado_ate = None
    controle.atualizado_em = agora

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
        .join(usuario_perfil, Perfil.id_perfil == usuario_perfil.c.id_perfil)
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
def me(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
