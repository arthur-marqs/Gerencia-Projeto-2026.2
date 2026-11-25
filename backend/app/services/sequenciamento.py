from itertools import pairwise
from uuid import UUID


def sugerir_sequencia(
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
