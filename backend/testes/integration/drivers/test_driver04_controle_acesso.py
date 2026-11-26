
"""Testes do Driver04: controle de acesso às operações protegidas."""

import pytest
from sqlalchemy import inspect, text


ID_INEXISTENTE = "00000000-0000-0000-0000-000000000001"

DETALHES_ESPERADOS = {
    "sem_sessao": "Sessão inválida ou expirada.",
    "operador": "Acesso não autorizado para este perfil.",
}

# Operações protegidas por PLANEJADOR.
# Os corpos vazios são intencionais: a autorização deve ser verificada
# antes que a operação seja executada ou que dados sejam alterados.
OPERACOES_PROTEGIDAS = [
    pytest.param("GET", "/api/maquinas", False, id="listar-maquinas"),
    pytest.param("POST", "/api/maquinas", True, id="cadastrar-maquina"),
    pytest.param("PUT", f"/api/maquinas/{ID_INEXISTENTE}", True, id="editar-maquina"),
    pytest.param("PATCH", f"/api/maquinas/{ID_INEXISTENTE}/status", True, id="alterar-status-maquina"),
    pytest.param("DELETE", f"/api/maquinas/{ID_INEXISTENTE}", False, id="excluir-maquina"),

    pytest.param("GET", "/api/families", False, id="listar-familias"),
    pytest.param("POST", "/api/families", True, id="cadastrar-familia"),

    pytest.param("GET", "/api/tempos-setup", False, id="listar-tempos-setup"),
    pytest.param("POST", "/api/tempos-setup", True, id="cadastrar-tempo-setup"),

    pytest.param("GET", "/api/produtos", False, id="listar-produtos"),
    pytest.param("POST", "/api/produtos", True, id="cadastrar-produto"),

    pytest.param("GET", "/api/ordens-producao", False, id="listar-ordens"),
    pytest.param("GET", f"/api/ordens-producao/{ID_INEXISTENTE}", False, id="consultar-ordem"),
    pytest.param("POST", "/api/ordens-producao", True, id="cadastrar-ordem"),
    pytest.param(
        "PATCH",
        f"/api/ordens-producao/{ID_INEXISTENTE}/duracao-estimada",
        True,
        id="alterar-duracao-ordem",
    ),
    pytest.param(
        "PUT",
        f"/api/ordens-producao/{ID_INEXISTENTE}",
        True,
        id="alterar-prazo-prioridade",
    ),

    pytest.param("GET", "/api/planejamentos", False, id="listar-planejamentos"),
    pytest.param(
        "GET",
        f"/api/planejamentos/{ID_INEXISTENTE}",
        False,
        id="consultar-planejamento",
    ),
    pytest.param("POST", "/api/planejamentos", True, id="criar-planejamento"),
    pytest.param(
        "PUT",
        f"/api/planejamentos/{ID_INEXISTENTE}",
        True,
        id="replanejar-sequencia",
    ),

    pytest.param(
        "POST",
        "/api/planejamentos/sugestoes",
        True,
        id="gerar-sugestao-sequencia",
    ),
    pytest.param(
        "GET",
        f"/api/planejamentos/sugestoes/{ID_INEXISTENTE}",
        False,
        id="consultar-sugestao-sequencia",
    ),
]


def _snapshot_banco(engine):
    """Captura os registros de todas as tabelas do banco de teste."""
    inspetor = inspect(engine)
    tabelas = sorted(inspetor.get_table_names())
    preparador = engine.dialect.identifier_preparer

    snapshot = {}

    with engine.connect() as conexao:
        for tabela in tabelas:
            nome_seguro = preparador.quote(tabela)
            registros = conexao.execute(
                text(f"SELECT * FROM {nome_seguro}")
            ).mappings().all()

            linhas = [
                tuple(sorted((coluna, repr(valor)) for coluna, valor in registro.items()))
                for registro in registros
            ]

            snapshot[tabela] = sorted(linhas, key=repr)

    return snapshot


@pytest.mark.parametrize(
    "tipo_acesso,status_esperado",
    [
        pytest.param("sem_sessao", 401, id="nao-autenticado"),
        pytest.param("operador", 403, id="operador-sem-permissao"),
    ],
)
@pytest.mark.parametrize(
    "metodo,caminho,possui_corpo",
    OPERACOES_PROTEGIDAS,
)
def test_driver04_bloqueia_operacao_sem_alterar_banco(
    seeded_auth,
    tipo_acesso,
    status_esperado,
    metodo,
    caminho,
    possui_corpo,
):
    client = seeded_auth.client
    state = seeded_auth.state

    # Garante que o primeiro cenário realmente não possui sessão.
    client.cookies.clear()

    if tipo_acesso == "operador":
        login = client.post(
            "/api/auth/login",
            json={
                "email": state.operator_email,
                "password": state.password,
            },
        )
        assert login.status_code == 200, login.text

    # O snapshot é feito depois do login para não confundir a criação
    # legítima da sessão com uma alteração causada pela tentativa.
    banco_antes = _snapshot_banco(state.engine)

    argumentos = {"json": {}} if possui_corpo else {}
    resposta = client.request(metodo, caminho, **argumentos)

    assert resposta.status_code == status_esperado, resposta.text
    assert resposta.json() == {
        "detail": DETALHES_ESPERADOS[tipo_acesso]
    }

    banco_depois = _snapshot_banco(state.engine)

    assert banco_depois == banco_antes, (
        f"O banco foi alterado após tentativa não autorizada: "
        f"{tipo_acesso} -> {metodo} {caminho}"
    )
