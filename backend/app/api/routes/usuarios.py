from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_profiles
from app.core.security import hash_password
from app.models.ordem_producao import OrdemProducao
from app.models.ordem_producao_operacao import OrdemProducaoOperacao
from app.models.perfil import Perfil
from app.models.planejamento import Planejamento
from app.models.sessao import Sessao
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioStatus, UsuarioUpdate


class RotaUsuarios(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def tratar(request):
            try:
                return await handler(request)
            except RequestValidationError as exc:
                # O FastAPI normalmente inclui o input; nunca devolver senhas,
                # nem mesmo quando o corpo inteiro é inválido.
                raise HTTPException(422, [
                    {"loc": erro["loc"], "msg": erro["msg"], "type": erro["type"]}
                    for erro in exc.errors()
                ]) from None
        return tratar


router = APIRouter(route_class=RotaUsuarios,
                   dependencies=[Depends(require_profiles("ADMINISTRADOR"))])
ULTIMO_ADMIN = "É necessário manter pelo menos um administrador ativo."


def administrar(
    token: str | None = Cookie(default=None, alias="setupflow_session"),
    db: Session = Depends(get_db),
) -> Usuario:
    # Serializa as alterações até o commit, inclusive sobre administradores distintos.
    # A autorização é conferida novamente após a espera por outra transação.
    db.execute(text("SELECT pg_advisory_xact_lock(320066)"))
    usuario = get_current_user(token=token, db=db)
    return require_profiles("ADMINISTRADOR")(usuario=usuario, db=db)


def buscar(db: Session, usuario_id: UUID, *, bloquear=False) -> Usuario:
    consulta = select(Usuario).where(Usuario.id_usuario == usuario_id)
    if bloquear:
        consulta = consulta.with_for_update().execution_options(populate_existing=True)
    usuario = db.scalar(consulta)
    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario


def perfis_usuario(db: Session, usuario_id: UUID) -> list[str]:
    return list(db.scalars(
        select(Perfil.codigo).join(usuario_perfil)
        .where(usuario_perfil.c.id_usuario == usuario_id).order_by(Perfil.codigo)
    ))


def apresentar(db: Session, usuario: Usuario) -> UsuarioRead:
    return UsuarioRead(
        id=usuario.id_usuario, nome=usuario.nome, email=usuario.email,
        ativo=usuario.ativo, perfis=perfis_usuario(db, usuario.id_usuario),
    )


def proteger_admin(db: Session, usuario: Usuario, *, ativo: bool, perfis: list[str]):
    if not usuario.ativo or "ADMINISTRADOR" not in perfis_usuario(db, usuario.id_usuario):
        return
    if ativo and "ADMINISTRADOR" in perfis:
        return
    outro_admin = db.scalar(
        select(Usuario.id_usuario).join(usuario_perfil).join(Perfil)
        .where(Usuario.ativo.is_(True), Perfil.codigo == "ADMINISTRADOR",
               Usuario.id_usuario != usuario.id_usuario).limit(1)
    )
    if outro_admin is None:
        raise HTTPException(409, ULTIMO_ADMIN)


def atribuir_perfis(db: Session, usuario: Usuario, codigos: list[str]):
    perfis = db.scalars(select(Perfil).where(Perfil.codigo.in_(codigos))).all()
    if len(perfis) != len(codigos):
        raise HTTPException(422, {"campos": {"perfis": "Selecione perfis válidos disponíveis no banco."}})
    db.execute(delete(usuario_perfil).where(usuario_perfil.c.id_usuario == usuario.id_usuario))
    db.execute(usuario_perfil.insert(), [
        {"id_usuario": usuario.id_usuario, "id_perfil": perfil.id_perfil} for perfil in perfis
    ])


def invalidar_sessoes(db: Session, usuario_id: UUID):
    db.execute(update(Sessao).where(
        Sessao.id_usuario == usuario_id, Sessao.invalidada_em.is_(None),
    ).values(invalidada_em=func.greatest(func.current_timestamp(), Sessao.criada_em)))


def salvar(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, {"campos": {"email": "O e-mail já está em uso."}}) from exc
        raise


def validar_email_disponivel(db: Session, email: str, usuario_id: UUID | None = None):
    if db.scalar(select(Usuario.id_usuario).where(
        Usuario.email == email, Usuario.id_usuario != usuario_id if usuario_id else True,
    )) is not None:
        raise HTTPException(409, {"campos": {"email": "O e-mail já está em uso."}})


def inserir(db: Session, usuario: Usuario):
    db.add(usuario)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, {"campos": {"email": "O e-mail já está em uso."}}) from exc
        raise


@router.get("", response_model=list[UsuarioRead])
def listar(db: Session = Depends(get_db)):
    usuarios = db.scalars(select(Usuario).order_by(Usuario.nome, Usuario.email)).all()
    return [apresentar(db, usuario) for usuario in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioRead)
def consultar(usuario_id: UUID, db: Session = Depends(get_db)):
    return apresentar(db, buscar(db, usuario_id))


@router.post("", response_model=UsuarioRead, status_code=201)
def cadastrar(dados: UsuarioCreate, db: Session = Depends(get_db),
              _admin: Usuario = Depends(administrar)):
    validar_email_disponivel(db, dados.email)
    usuario = Usuario(nome=dados.nome, email=dados.email,
                      senha_hash=hash_password(dados.senha), ativo=True)
    inserir(db, usuario)
    atribuir_perfis(db, usuario, dados.perfis)
    salvar(db)
    return apresentar(db, usuario)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def alterar(usuario_id: UUID, dados: UsuarioUpdate, db: Session = Depends(get_db),
            _admin: Usuario = Depends(administrar)):
    usuario = buscar(db, usuario_id, bloquear=True)
    proteger_admin(db, usuario, ativo=usuario.ativo, perfis=dados.perfis)
    validar_email_disponivel(db, dados.email, usuario_id)
    atribuir_perfis(db, usuario, dados.perfis)
    usuario.nome, usuario.email = dados.nome, dados.email
    if dados.senha is not None:
        usuario.senha_hash = hash_password(dados.senha)
        invalidar_sessoes(db, usuario_id)
    salvar(db)
    return apresentar(db, usuario)


@router.patch("/{usuario_id}/status", response_model=UsuarioRead)
def alterar_status(usuario_id: UUID, dados: UsuarioStatus, db: Session = Depends(get_db),
                   _admin: Usuario = Depends(administrar)):
    usuario = buscar(db, usuario_id, bloquear=True)
    proteger_admin(db, usuario, ativo=dados.ativo, perfis=perfis_usuario(db, usuario_id))
    usuario.ativo = dados.ativo
    if not dados.ativo:
        invalidar_sessoes(db, usuario_id)
    salvar(db)
    return apresentar(db, usuario)


@router.delete("/{usuario_id}", status_code=204)
def excluir(usuario_id: UUID, db: Session = Depends(get_db),
            _admin: Usuario = Depends(administrar)):
    usuario = buscar(db, usuario_id, bloquear=True)
    proteger_admin(db, usuario, ativo=False, perfis=[])
    vinculos = []
    for campo, descricao in (
        (OrdemProducao.criado_por, "ordens de produção"),
        (Planejamento.criado_por, "planejamentos"),
        (OrdemProducaoOperacao.usuario_id, "operações de ordens de produção"),
    ):
        if db.scalar(select(campo).where(campo == usuario_id).limit(1)) is not None:
            vinculos.append(descricao)
    if vinculos:
        raise HTTPException(409, {
            "mensagem": f"Exclusão impedida por vínculos com {', '.join(vinculos)}.",
            "vinculos": vinculos, "pode_desativar": usuario.ativo,
        })
    db.delete(usuario)
    salvar(db)
    return Response(status_code=204)
