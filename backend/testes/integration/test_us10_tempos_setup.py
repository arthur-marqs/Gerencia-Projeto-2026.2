from uuid import uuid4

import pytest
from sqlalchemy import text


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def _criar_familia(client, codigo: str, nome: str):
    response = client.post(
        "/api/families",
        json={"code": codigo, "name": nome},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _cadastrar_tempo_setup(client, origem_id: str, destino_id: str, tempo):
    return client.post(
        "/api/tempos-setup",
        json={
            "familia_origem_id": origem_id,
            "familia_destino_id": destino_id,
            "tempo_setup_minutos": tempo,
        },
    )


def _preparar_familias(client):
    origem = _criar_familia(client, "FAM-US10-A", "Família US10 A")
    destino = _criar_familia(client, "FAM-US10-B", "Família US10 B")
    return origem, destino


def test_planejador_cadastra_tempo_setup_valido(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    origem, destino = _preparar_familias(client)

    response = _cadastrar_tempo_setup(
        client,
        origem["id"],
        destino["id"],
        45,
    )

    assert response.status_code == 201, response.text
    cadastro = response.json()
    assert cadastro["familia_origem"]["id"] == origem["id"]
    assert cadastro["familia_origem"]["name"] == origem["name"]
    assert cadastro["familia_destino"]["id"] == destino["id"]
    assert cadastro["familia_destino"]["name"] == destino["name"]
    assert cadastro["tempo_setup_minutos"] == 45

    listagem = client.get("/api/tempos-setup")
    assert listagem.status_code == 200
    assert len(listagem.json()) == 1
    assert listagem.json()[0]["tempo_setup_minutos"] == 45

    with state.engine.connect() as connection:
        salvo = connection.execute(
            text(
                """
                SELECT tempo_setup_minutos
                FROM tempos_setup_familias
                WHERE familia_origem_id = :origem_id
                  AND familia_destino_id = :destino_id
                """
            ),
            {"origem_id": origem["id"], "destino_id": destino["id"]},
        ).scalar_one()
    assert salvo == 45


@pytest.mark.parametrize("tempo_invalido", [0, -1, 1.5, "inválido", None, True])
def test_tempo_setup_invalido_nao_e_salvo(seeded_auth, tempo_invalido):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    origem, destino = _preparar_familias(client)

    response = _cadastrar_tempo_setup(
        client,
        origem["id"],
        destino["id"],
        tempo_invalido,
    )

    assert response.status_code == 422
    assert "tempo de setup informado é inválido" in str(response.json()).lower()

    with state.engine.connect() as connection:
        quantidade = connection.execute(
            text("SELECT count(*) FROM tempos_setup_familias")
        ).scalar_one()
    assert quantidade == 0


def test_familias_de_origem_e_destino_devem_ser_diferentes(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    familia = _criar_familia(client, "FAM-US10-C", "Família US10 C")

    response = _cadastrar_tempo_setup(
        client,
        familia["id"],
        familia["id"],
        30,
    )

    assert response.status_code == 422
    assert "famílias de origem e destino devem ser diferentes" in str(response.json()).lower()


def test_familia_inexistente_retorna_404(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    destino = _criar_familia(client, "FAM-US10-D", "Família US10 D")

    response = _cadastrar_tempo_setup(
        client,
        str(uuid4()),
        destino["id"],
        30,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Família de origem não encontrada."


def test_combinacao_de_familias_nao_pode_ser_cadastrada_duas_vezes(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    origem, destino = _preparar_familias(client)

    primeiro = _cadastrar_tempo_setup(client, origem["id"], destino["id"], 20)
    segundo = _cadastrar_tempo_setup(client, origem["id"], destino["id"], 35)

    assert primeiro.status_code == 201, primeiro.text
    assert segundo.status_code == 409
    assert segundo.json()["detail"] == (
        "Já existe um tempo de setup configurado entre essas famílias."
    )


def test_tempo_setup_e_direcional_por_combinacao_de_familias(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    origem, destino = _preparar_familias(client)

    ida = _cadastrar_tempo_setup(client, origem["id"], destino["id"], 20)
    volta = _cadastrar_tempo_setup(client, destino["id"], origem["id"], 35)

    assert ida.status_code == 201, ida.text
    assert volta.status_code == 201, volta.text
    assert ida.json()["tempo_setup_minutos"] == 20
    assert volta.json()["tempo_setup_minutos"] == 35


def test_cadastro_de_tempo_setup_exige_autenticacao(seeded_auth):
    response = _cadastrar_tempo_setup(
        seeded_auth.client,
        str(uuid4()),
        str(uuid4()),
        30,
    )

    assert response.status_code == 401


def test_operador_nao_pode_cadastrar_tempo_setup(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = _cadastrar_tempo_setup(
        client,
        str(uuid4()),
        str(uuid4()),
        30,
    )

    assert response.status_code == 403


def test_consulta_tempos_setup_exige_autenticacao(seeded_auth):
    response = seeded_auth.client.get("/api/tempos-setup")

    assert response.status_code == 401


def test_operador_nao_pode_consultar_tempos_setup(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.operator_email, state.password).status_code == 200

    response = client.get("/api/tempos-setup")

    assert response.status_code == 403


def test_familia_destino_inexistente_retorna_404(seeded_auth):
    client, state = seeded_auth.client, seeded_auth.state
    assert _login(client, state.email, state.password).status_code == 200
    origem = _criar_familia(client, "FAM-US10-E", "Família US10 E")

    response = _cadastrar_tempo_setup(
        client,
        origem["id"],
        str(uuid4()),
        30,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Família de destino não encontrada."
