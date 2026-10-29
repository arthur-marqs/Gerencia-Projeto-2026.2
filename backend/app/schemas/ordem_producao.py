from datetime import datetime
from decimal import Decimal
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
