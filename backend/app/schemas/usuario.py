import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


PerfilCodigo = Literal["ADMINISTRADOR", "PLANEJADOR", "OPERADOR"]


class UsuarioDados(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    nome: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=1, max_length=254)
    perfis: list[PerfilCodigo] = Field(min_length=1)

    @field_validator("nome", "email", mode="before")
    @classmethod
    def normalizar(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Informe um e-mail válido.")
        return value

    @field_validator("perfis")
    @classmethod
    def perfis_unicos(cls, value):
        return sorted(set(value))


class UsuarioCreate(UsuarioDados):
    senha: str = Field(min_length=8, repr=False)


class UsuarioUpdate(UsuarioDados):
    senha: str | None = Field(default=None, repr=False)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, value):
        if value == "" or value is None:
            return None
        if len(value) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        return value


class UsuarioStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ativo: bool = Field(strict=True)


class UsuarioRead(BaseModel):
    id: UUID
    nome: str
    email: str
    perfis: list[str]
    ativo: bool
