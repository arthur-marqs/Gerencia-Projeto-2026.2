from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.perfil import Perfil
from app.models.usuario import Usuario
from app.models.usuario_perfil import usuario_perfil


def main() -> None:
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    perfil_codigo = input("Perfil (PLANEJADOR ou OPERADOR): ").strip().upper()

    senha = getpass("Senha: ")
    confirmacao = getpass("Confirme a senha: ")

    if not nome or not email:
        raise SystemExit("Nome e e-mail são obrigatórios.")

    if perfil_codigo not in {"PLANEJADOR", "OPERADOR"}:
        raise SystemExit("Perfil inválido.")

    if not senha:
        raise SystemExit("A senha não pode ficar vazia.")

    if senha != confirmacao:
        raise SystemExit("As senhas não coincidem.")

    with SessionLocal() as session:
        usuario_existente = session.scalar(
            select(Usuario).where(Usuario.email == email)
        )

        if usuario_existente:
            raise SystemExit("Já existe um usuário com esse e-mail.")

        perfil = session.scalar(
            select(Perfil).where(Perfil.codigo == perfil_codigo)
        )

        if not perfil:
            raise SystemExit(f"O perfil {perfil_codigo} não existe no banco.")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            ativo=True,
        )

        session.add(usuario)
        session.flush()

        session.execute(
            usuario_perfil.insert().values(
                id_usuario=usuario.id_usuario,
                id_perfil=perfil.id_perfil,
            )
        )

        session.commit()

    print(f"Usuário {email} criado com o perfil {perfil_codigo}.")


if __name__ == "__main__":
    main()