from datetime import date, datetime
from uuid import UUID

from app.services.sequenciamento import DadosSequenciamento, sugerir_sequencia


OP1, OP2, OP3 = (UUID(int=i) for i in range(1, 4))
A, B = UUID(int=10), UUID(int=20)
INICIO = datetime(2026, 11, 25, 23, 0)


def test_prioridade_alta_pode_justificar_setup_maior():
    familias = {OP1: A, OP2: A, OP3: B}
    tempos = {(A, B): 5, (B, A): 30}

    dados = {
        OP1: DadosSequenciamento(date(2026, 11, 30), "Baixa", 30),
        OP2: DadosSequenciamento(date(2026, 11, 30), "Média", 30),
        OP3: DadosSequenciamento(date(2026, 11, 25), "Alta", 40),
    }

    assert sugerir_sequencia(
        familias, tempos, dados_por_ordem=dados, inicio=INICIO
    ) == (
        [OP3, OP2, OP1], [0, 30, 0], 5,
    )


def test_prazo_restritivo_pode_antecipar_ordem_de_prioridade_baixa():
    dados = {
        OP1: DadosSequenciamento(date(2026, 11, 30), "Alta", 40),
        OP2: DadosSequenciamento(date(2026, 11, 25), "Baixa", 40),
    }

    sequencia, _, _ = sugerir_sequencia(
        {OP1: A, OP2: A},
        {},
        dados_por_ordem=dados,
        inicio=INICIO,
    )

    assert sequencia == [OP2, OP1]


def test_prioridade_influencia_sem_risco_de_atraso():
    dados = {
        OP1: DadosSequenciamento(date(2026, 11, 30), "Baixa", 20),
        OP2: DadosSequenciamento(date(2026, 11, 30), "Alta", 20),
    }

    sequencia, _, _ = sugerir_sequencia(
        {OP1: A, OP2: A},
        {},
        dados_por_ordem=dados,
        inicio=INICIO,
    )

    assert sequencia == [OP2, OP1]


def test_sem_dados_de_urgencia_preserva_us13():
    assert sugerir_sequencia(
        {OP1: A, OP2: B, OP3: A},
        {(A, B): 5, (B, A): 30},
    ) == (
        [OP1, OP3, OP2], [0, 0, 5], 35,
    )
