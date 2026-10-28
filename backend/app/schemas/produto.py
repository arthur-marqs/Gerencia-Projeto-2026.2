from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    nome: str = Field(min_length=1, max_length=150)
    unidade: str = Field(min_length=1, max_length=20)

    @field_validator("codigo", "nome", "unidade", mode="before")
    @classmethod
    def remover_espacos(cls, valor: str) -> str:
        if isinstance(valor, str):
            return valor.strip()

        return valor


class ProdutoFamiliaUpdate(BaseModel):
    family_id: UUID | None


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto: UUID
    codigo: str
    nome: str
    unidade: str
    family_id: UUID | None
    ativo: bool
    criado_em: datetime
