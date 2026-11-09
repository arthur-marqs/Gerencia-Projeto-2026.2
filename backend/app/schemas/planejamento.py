
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlanejamentoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    ordens_ids: list[UUID] = Field(min_length=1)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        nome = valor.strip()

        if not nome:
            raise ValueError("O nome do planejamento é obrigatório.")

        return nome

    @field_validator("ordens_ids")
    @classmethod
    def validar_ordens(cls, valores: list[UUID]) -> list[UUID]:
        if len(valores) != len(set(valores)):
            raise ValueError(
                "Uma ordem não pode aparecer mais de uma vez no planejamento."
            )

        return valores


class ItemPlanejamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_item: UUID
    ordem_id: UUID
    posicao: int


class PlanejamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_planejamento: UUID
    nome: str
    criado_por: UUID
    criado_em: datetime
    itens: list[ItemPlanejamentoResponse]

class PlanejamentoUpdate(PlanejamentoCreate):
    pass
