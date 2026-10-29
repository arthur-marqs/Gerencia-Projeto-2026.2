from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrdemProducaoCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    produto_id: UUID
    quantidade: Decimal = Field(gt=0, max_digits=14, decimal_places=3)

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo(cls, valor: str) -> str:
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor


class OrdemProducaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_ordem: UUID
    codigo: str
    produto_id: UUID
    quantidade: Decimal
    status: str
    criado_em: datetime
    prazo: date | None
    prioridade: str | None


class OrdemProducaoUpdate(BaseModel):
    prazo: date
    prioridade: Literal["Baixa", "Média", "Alta"]

    @field_validator("prazo", mode="before")
    @classmethod
    def validar_prazo_obrigatorio(cls, valor: object) -> object:
        if valor is None or valor == "":
            raise ValueError("O prazo é obrigatório.")
        return valor

    @field_validator("prazo")
    @classmethod
    def validar_prazo_nao_passado(cls, valor: date) -> date:
        if valor < date.today():
            raise ValueError("O prazo não pode estar no passado.")
        return valor

    @field_validator("prioridade", mode="before")
    @classmethod
    def validar_prioridade(cls, valor: object) -> object:
        if not isinstance(valor, str) or valor not in {"Baixa", "Média", "Alta"}:
            raise ValueError(
                "Uma prioridade válida entre Baixa, Média e Alta é obrigatória."
            )
        return valor
