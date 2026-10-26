import pytest
from fastapi import HTTPException
from sqlalchemy import text


def test_planejador_acessa_recurso_permitido(auth_test_context, auth_state):
    from app.api.deps import require_profiles
    from app.models.usuario import Usuario

    with auth_test_context.factory() as db:
        usuario = db.get(Usuario, auth_state.user_id)

        verificar_perfil = require_profiles("PLANEJADOR")
        resultado = verificar_perfil(usuario=usuario, db=db)

        assert resultado.id_usuario == auth_state.user_id


def test_operador_nao_acessa_recurso_exclusivo_de_planejador(
    auth_test_context,
    auth_state,
):
    from app.api.deps import require_profiles
    from app.models.usuario import Usuario

    with auth_test_context.factory() as db:
        usuario = db.get(Usuario, auth_state.operator_user_id)

        verificar_perfil = require_profiles("PLANEJADOR")

        with pytest.raises(HTTPException) as erro:
            verificar_perfil(usuario=usuario, db=db)

        assert erro.value.status_code == 403
        assert erro.value.detail == "Acesso não autorizado para este perfil."


def test_operador_acessa_recurso_permitido(auth_test_context, auth_state):
    from app.api.deps import require_profiles
    from app.models.usuario import Usuario

    with auth_test_context.factory() as db:
        usuario = db.get(Usuario, auth_state.operator_user_id)

        verificar_perfil = require_profiles("OPERADOR")
        resultado = verificar_perfil(usuario=usuario, db=db)

        assert resultado.id_usuario == auth_state.operator_user_id


def test_usuario_com_multiplos_perfis_acessa_por_qualquer_perfil(
    auth_test_context,
    auth_state,
):
    with auth_test_context.engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO usuario_perfil (id_usuario, id_perfil)
                SELECT :user_id, id_perfil
                FROM perfis
                WHERE codigo = 'OPERADOR'
                ON CONFLICT DO NOTHING
                """
            ),
            {"user_id": auth_state.user_id},
        )

    from app.api.deps import require_profiles
    from app.models.usuario import Usuario

    with auth_test_context.factory() as db:
        usuario = db.get(Usuario, auth_state.user_id)

        verificar_perfil = require_profiles("OPERADOR")
        resultado = verificar_perfil(usuario=usuario, db=db)

        assert resultado.id_usuario == auth_state.user_id
