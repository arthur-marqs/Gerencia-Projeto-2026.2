from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from itertools import pairwise
from uuid import UUID

def _sugerir_por_setup(
    familias_por_ordem: dict[UUID, UUID],
    tempos: dict[tuple[UUID, UUID], int],
) -> tuple[list[UUID], list[int], int]:
    """Retorna a sequência, o setup por posição e o total da sequência original."""
    ordens_por_familia: dict[UUID, list[UUID]] = {}
    for ordem, familia in familias_por_ordem.items():
        ordens_por_familia.setdefault(familia, []).append(ordem)

    sequencia = list(familias_por_ordem)
    total_original = melhor_total = sum(calcular_setups(sequencia, familias_por_ordem, tempos))

    # Testa um caminho guloso a partir de cada família, com desempate pela seleção.
    for primeira in ordens_por_familia:
        if melhor_total == 0:
            break

        restantes = dict.fromkeys(f for f in ordens_por_familia if f != primeira)
        caminho = [primeira]
        total = 0
        while restantes and total < melhor_total:
            atual = caminho[-1]
            proxima = min(restantes, key=lambda familia: tempos[atual, familia])
            total += tempos[atual, proxima]
            caminho.append(proxima)
            del restantes[proxima]

        if total < melhor_total:
            melhor_total = total
            sequencia = [ordem for familia in caminho for ordem in ordens_por_familia[familia]]

    return sequencia, calcular_setups(sequencia, familias_por_ordem, tempos), total_original


def calcular_setups(
    sequencia: list[UUID],
    familias_por_ordem: dict[UUID, UUID],
    tempos: dict[tuple[UUID, UUID], int],
) -> list[int]:
    if not sequencia:
        return []

    familias = [familias_por_ordem[ordem] for ordem in sequencia]
    return [0] + [
        tempos[origem, destino] if origem != destino else 0
        for origem, destino in pairwise(familias)
    ]

@dataclass(frozen=True)
class DadosSequenciamento:
    prazo: date
    prioridade: str
    duracao_estimada_minutos: int


def sugerir_sequencia(
    familias_por_ordem: dict[UUID, UUID],
    tempos: dict[tuple[UUID, UUID], int],
    *,
    dados_por_ordem: dict[UUID, DadosSequenciamento] | None = None,
    inicio: datetime | None = None,
) -> tuple[list[UUID], list[int], int]:
    """Sugere uma sequência considerando setup e, quando informada, urgência."""
    por_setup, setups, total_original = _sugerir_por_setup(
        familias_por_ordem, tempos
    )

    if dados_por_ordem is None:
        return por_setup, setups, total_original

    if inicio is None or dados_por_ordem.keys() != familias_por_ordem.keys():
        raise ValueError("Informe o início e os dados de todas as ordens.")

    prioridades = {"Alta": 0, "Média": 1, "Baixa": 2}
    original = list(familias_por_ordem)

    prioridade = {
        o: prioridades[dados_por_ordem[o].prioridade]
        for o in original
    }

    duracao = {
        o: dados_por_ordem[o].duracao_estimada_minutos * 60
        for o in original
    }

    prazo = {
        o: (
            datetime.combine(
                dados_por_ordem[o].prazo,
                time.min,
                tzinfo=inicio.tzinfo,
            )
            - inicio + timedelta(days=1)
        ).total_seconds()
        for o in original
    }

    def setup_entre(anterior: UUID | None, ordem: UUID) -> int:
        if anterior is None:
            return 0

        origem = familias_por_ordem[anterior]
        destino = familias_por_ordem[ordem]

        return tempos[origem, destino] if origem != destino else 0

    # A folga indica quanto tempo resta antes de a ordem correr risco de atraso.
    restantes = original.copy()
    por_folga: list[UUID] = []
    decorrido = 0

    while restantes:
        anterior = por_folga[-1] if por_folga else None

        ordem = min(restantes, key=lambda o: (
            prazo[o] - decorrido - duracao[o] - setup_entre(anterior, o) * 60,
            prioridade[o],
            setup_entre(anterior, o),
        ))

        decorrido += duracao[ordem] + setup_entre(anterior, ordem) * 60
        por_folga.append(ordem)
        restantes.remove(ordem)

    def avaliar(sequencia: list[UUID]) -> tuple:
        atrasadas = [0, 0, 0]
        atrasos = [0.0, 0.0, 0.0]
        decorrido = 0

        setups = calcular_setups(
            sequencia, familias_por_ordem, tempos
        )

        for ordem, setup in zip(sequencia, setups, strict=True):
            decorrido += setup * 60 + duracao[ordem]
            atraso = max(0, decorrido - prazo[ordem])

            if atraso:
                atrasadas[prioridade[ordem]] += 1
                atrasos[prioridade[ordem]] += atraso

        inversoes_prioridade = sum(
            prioridade[a] > prioridade[b]
            for i, a in enumerate(sequencia)
            for b in sequencia[i + 1:]
        )

        inversoes_prazo = sum(
            prazo[a] > prazo[b]
            for i, a in enumerate(sequencia)
            for b in sequencia[i + 1:]
        )

        return (
            sum(atrasadas),
            atrasadas[0],
            atrasadas[1],
            *atrasos,
            inversoes_prioridade,
            sum(setups),
            inversoes_prazo,
        )

    alternativas = [
        original,
        por_setup,
        sorted(original, key=lambda o: (prazo[o], prioridade[o])),
        sorted(original, key=lambda o: (prioridade[o], prazo[o])),
        por_folga,
    ]

    sequencia = min(alternativas, key=avaliar)

    return (
        sequencia,
        calcular_setups(sequencia, familias_por_ordem, tempos),
        total_original,
    )
