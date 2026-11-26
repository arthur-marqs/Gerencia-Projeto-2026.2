from datetime import datetime
from uuid import UUID

from app.services.sequenciamento import DadosSequenciamento, calcular_setups, sugerir_sequencia


def calcular_setup_por_maquina(
    sequencia: list[UUID],
    familias_por_ordem: dict[UUID, UUID],
    maquinas_por_ordem: dict[UUID, UUID | None],
    tempos: dict[tuple[UUID, UUID], int],
) -> int:
    ordens_por_maquina: dict[UUID | None, list[UUID]] = {}
    for ordem_id in sequencia:
        maquina_id = maquinas_por_ordem[ordem_id]
        ordens_por_maquina.setdefault(maquina_id, []).append(ordem_id)

    return sum(
        sum(calcular_setups(ordens, familias_por_ordem, tempos))
        for ordens in ordens_por_maquina.values()
    )


def sugerir_sequencia_por_maquina(
    familias_por_ordem: dict[UUID, UUID],
    maquinas_por_ordem: dict[UUID, UUID],
    tempos: dict[tuple[UUID, UUID], int],
    *,
    dados_por_ordem: dict[UUID, DadosSequenciamento] | None = None,
    inicio: datetime | None = None,
) -> tuple[list[UUID], list[int], int]:
    """Gera a sequência de cada máquina considerando setup e urgência."""

    if familias_por_ordem.keys() != maquinas_por_ordem.keys():
        raise ValueError("Todas as ordens devem possuir uma máquina atribuída.")

    if dados_por_ordem is not None and (
        inicio is None or dados_por_ordem.keys() != familias_por_ordem.keys()
    ):
        raise ValueError("Informe o início e os dados de todas as ordens.")

    ordens_por_maquina: dict[UUID, dict[UUID, UUID]] = {}

    for ordem_id, familia_id in familias_por_ordem.items():
        maquina_id = maquinas_por_ordem[ordem_id]

        ordens_por_maquina.setdefault(maquina_id, {})[ordem_id] = familia_id

    sequencia: list[UUID] = []
    setups: list[int] = []
    total_original = 0

    for ordens in ordens_por_maquina.values():
        dados_maquina = (
            {ordem_id: dados_por_ordem[ordem_id] for ordem_id in ordens}
            if dados_por_ordem is not None
            else None
        )
        sequencia_maquina, setups_maquina, original_maquina = sugerir_sequencia(
            ordens,
            tempos,
            dados_por_ordem=dados_maquina,
            inicio=inicio,
        )

        sequencia.extend(sequencia_maquina)
        setups.extend(setups_maquina)
        total_original += original_maquina

    return sequencia, setups, total_original
