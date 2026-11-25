from collections import Counter, defaultdict
from collections.abc import Iterator
from uuid import UUID


def distribuir_ordens(
    maquinas_por_ordem: dict[UUID, dict[UUID, str]],
) -> dict[UUID, UUID]:
    """Distribui as ordens entre as máquinas compatíveis."""

    distribuicao: dict[UUID, UUID] = {}
    quantidade_por_maquina: Counter[UUID] = Counter()

    for ordem_id, maquinas in maquinas_por_ordem.items():
        if not maquinas:
            raise ValueError(
                f"A ordem {ordem_id} não possui máquina compatível."
            )

        maquina_id = min(
            maquinas,
            key=lambda m: (
                quantidade_por_maquina[m],
                maquinas[m],
            ),
        )

        distribuicao[ordem_id] = maquina_id
        quantidade_por_maquina[maquina_id] += 1

    return distribuicao


def redistribuir_com_setups_cadastrados(
    maquinas_por_ordem: dict[UUID, dict[UUID, str]],
    familias_por_ordem: dict[UUID, UUID],
    tempos: dict[tuple[UUID, UUID], int],
) -> dict[UUID, UUID] | None:
    """Procura uma distribuição com os dois sentidos de setup para cada máquina."""
    ordens_equivalentes: dict[tuple[UUID, frozenset[UUID]], list[UUID]] = {}
    for ordem_id, maquinas in maquinas_por_ordem.items():
        chave = (familias_por_ordem[ordem_id], frozenset(maquinas))
        ordens_equivalentes.setdefault(chave, []).append(ordem_id)

    # Ordens da mesma família com as mesmas opções podem compartilhar a máquina.
    grupos = sorted(
        ordens_equivalentes.values(),
        key=lambda ordens: len(maquinas_por_ordem[ordens[0]]),
    )
    familias_por_maquina: dict[UUID, Counter[UUID]] = defaultdict(Counter)
    quantidade_por_maquina: Counter[UUID] = Counter()

    def maquinas_elegiveis(ordem_id: UUID) -> Iterator[UUID]:
        familia = familias_por_ordem[ordem_id]
        maquinas = maquinas_por_ordem[ordem_id]
        return iter(sorted(
            (
                maquina for maquina in maquinas
                if all(
                    outra == familia
                    or ((familia, outra) in tempos and (outra, familia) in tempos)
                    for outra in familias_por_maquina[maquina]
                )
            ),
            key=lambda maquina: (quantidade_por_maquina[maquina], maquinas[maquina]),
        ))

    # Se um grupo ficar sem opções, volte à escolha anterior e tente outra máquina.
    tentativas: list[Iterator[UUID]] = []
    maquinas_escolhidas: list[UUID] = []
    while len(maquinas_escolhidas) < len(grupos):
        indice = len(maquinas_escolhidas)
        grupo = grupos[indice]
        if len(tentativas) == indice:
            tentativas.append(maquinas_elegiveis(grupo[0]))

        maquina = next(tentativas[-1], None)
        if maquina is None:
            tentativas.pop()
            if not maquinas_escolhidas:
                return None
            anterior = maquinas_escolhidas.pop()
            grupo_anterior = grupos[indice - 1]
            familia_anterior = familias_por_ordem[grupo_anterior[0]]
            familias_por_maquina[anterior][familia_anterior] -= 1
            if familias_por_maquina[anterior][familia_anterior] == 0:
                del familias_por_maquina[anterior][familia_anterior]
            quantidade_por_maquina[anterior] -= len(grupo_anterior)
            continue

        maquinas_escolhidas.append(maquina)
        familias_por_maquina[maquina][familias_por_ordem[grupo[0]]] += 1
        quantidade_por_maquina[maquina] += len(grupo)

    return {
        ordem_id: maquina
        for grupo, maquina in zip(grupos, maquinas_escolhidas, strict=True)
        for ordem_id in grupo
    }
