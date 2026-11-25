from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.services.distribuicao_maquinas import distribuir_ordens
from app.services.sequenciamento import DadosSequenciamento
from app.services.sequenciamento_maquinas import sugerir_sequencia_por_maquina


def test_ordem_atribuida_a_unica_maquina_compativel():
    ordem = uuid4()
    maquina = uuid4()

    resultado = distribuir_ordens({
        ordem: {maquina: "M01"},
    })

    assert resultado == {ordem: maquina}


def test_distribuicao_entre_maquinas_compativeis():
    op1, op2, op3 = uuid4(), uuid4(), uuid4()
    m1, m2 = uuid4(), uuid4()

    resultado = distribuir_ordens({
        op1: {m2: "M02", m1: "M01"},
        op2: {m1: "M01", m2: "M02"},
        op3: {m1: "M01", m2: "M02"},
    })

    assert resultado == {
        op1: m1,
        op2: m2,
        op3: m1,
    }


def test_ordem_sem_maquina_compativel():
    ordem = uuid4()

    with pytest.raises(ValueError, match="não possui máquina compatível"):
        distribuir_ordens({ordem: {}})


def test_nao_calcula_setup_entre_maquinas_diferentes():
    op1, op2 = uuid4(), uuid4()
    familia_a, familia_b = uuid4(), uuid4()
    m1, m2 = uuid4(), uuid4()

    sequencia, setups, original = sugerir_sequencia_por_maquina(
        {op1: familia_a, op2: familia_b},
        {op1: m1, op2: m2},
        {},
    )

    assert sequencia == [op1, op2]
    assert setups == [0, 0]
    assert original == 0


def test_otimiza_setup_individualmente_por_maquina():
    op1, op2, op3, op4 = [uuid4() for _ in range(4)]
    familia_a, familia_b, familia_c = uuid4(), uuid4(), uuid4()
    m1, m2 = uuid4(), uuid4()

    sequencia, setups, original = sugerir_sequencia_por_maquina(
        {
            op1: familia_a,
            op2: familia_b,
            op3: familia_a,
            op4: familia_c,
        },
        {
            op1: m1,
            op2: m1,
            op3: m1,
            op4: m2,
        },
        {
            (familia_a, familia_b): 20,
            (familia_b, familia_a): 30,
        },
    )

    assert sequencia == [op1, op3, op2, op4]
    assert setups == [0, 0, 20, 0]
    assert original == 50
    assert sum(setups) == 20


def test_rejeita_ordem_sem_maquina_atribuida():
    ordem, familia = uuid4(), uuid4()

    with pytest.raises(ValueError, match="máquina atribuída"):
        sugerir_sequencia_por_maquina(
            {ordem: familia},
            {},
            {},
        )



def test_urgencia_independente_por_maquina():
    op1, op2, op3, op4 = [uuid4() for _ in range(4)]
    a, b, c, m1, m2 = [uuid4() for _ in range(5)]
    inicio = datetime(2026, 11, 25, 23)
    dia = inicio.date()
    futuro = dia + timedelta(days=1)

    resultado = sugerir_sequencia_por_maquina(
        {op1: a, op3: c, op2: b, op4: c},
        {op1: m1, op3: m2, op2: m1, op4: m2},
        {(a, b): 5, (b, a): 30},
        dados_por_ordem={
            op1: DadosSequenciamento(futuro, "Baixa", 30),
            op2: DadosSequenciamento(dia, "Alta", 40),
            op3: DadosSequenciamento(futuro, "Alta", 40),
            op4: DadosSequenciamento(dia, "Baixa", 40),
        },
        inicio=inicio,
    )

    assert resultado == ([op2, op1, op4, op3], [0, 30, 0, 0], 5)


@pytest.mark.parametrize("sem_inicio", [False, True])
def test_rejeita_dados_de_urgencia_incompletos(sem_inicio):
    op1, op2, a, m1, m2 = [uuid4() for _ in range(5)]
    inicio = datetime(2026, 11, 25, 23)
    dados = {op1: DadosSequenciamento(inicio.date(), "Alta", 30)}

    if sem_inicio:
        dados[op2] = DadosSequenciamento(inicio.date(), "Baixa", 20)

    with pytest.raises(ValueError, match="Informe o início e os dados de todas as ordens"):
        sugerir_sequencia_por_maquina(
            {op1: a, op2: a},
            {op1: m1, op2: m2},
            {},
            dados_por_ordem=dados,
            inicio=None if sem_inicio else inicio,
        )
