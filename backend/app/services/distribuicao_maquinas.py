from collections import Counter
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
