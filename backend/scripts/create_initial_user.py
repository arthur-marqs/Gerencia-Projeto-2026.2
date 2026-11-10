from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.perfil import Perfil
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil
from app.schemas.usuario import UsuarioCreate


def main() -> None:
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    perfil_codigo = input("Perfis (ADMINISTRADOR, PLANEJADOR, OPERADOR; separe por vírgula): ")

    senha = getpass("Senha: ")
    confirmacao = getpass("Confirme a senha: ")

    if senha != confirmacao:
        raise SystemExit("As senhas não coincidem.")

    try:
        dados = UsuarioCreate(nome=nome, email=email, senha=senha,
                              perfis=[codigo.strip().upper() for codigo in perfil_codigo.split(",")])
    except ValidationError as exc:
        # Não imprime os valores de entrada, em especial a senha.
        raise SystemExit("Dados inválidos: " + "; ".join(
            f"{erro['loc'][0]}: {erro['msg']}" for erro in exc.errors(include_input=False)
        )) from None

    nome, email = dados.nome, dados.email

    with SessionLocal() as session:
        session.execute(text("SELECT pg_advisory_xact_lock(320066)"))
        usuario_existente = session.scalar(
            select(Usuario).where(Usuario.email == email)
        )

        if usuario_existente:
            raise SystemExit("Já existe um usuário com esse e-mail.")

        perfis = session.scalars(select(Perfil).where(Perfil.codigo.in_(dados.perfis))).all()

        if len(perfis) != len(dados.perfis):
            raise SystemExit("Perfil indisponível. Execute alembic upgrade head primeiro.")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            ativo=True,
        )

        session.add(usuario)
        try:
            session.flush()
            session.execute(usuario_perfil.insert(), [
                {"id_usuario": usuario.id_usuario, "id_perfil": perfil.id_perfil}
                for perfil in perfis
            ])
            session.commit()
        except IntegrityError:
            session.rollback()
            raise SystemExit("Não foi possível cadastrar: e-mail já em uso ou perfil indisponível.") from None

    print(f"Usuário {email} criado com os perfis {', '.join(dados.perfis)}.")


if __name__ == "__main__":
    main()
