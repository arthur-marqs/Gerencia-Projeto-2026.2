from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MaquinaCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    nome: str = Field(min_length=1, max_length=150)
    descricao: str | None = None

    @field_validator("codigo", "nome", "descricao", mode="before")
    @classmethod
    def remover_espacos(cls, valor: str | None) -> str | None:
        if isinstance(valor, str):
            return valor.strip()

        return valor


class MaquinaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_maquina: UUID
    codigo: str
    nome: str
    descricao: str | None
    ativo: bool
    criado_em: datetime
