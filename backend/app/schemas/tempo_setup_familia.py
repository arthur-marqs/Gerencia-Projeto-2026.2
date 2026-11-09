from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TempoSetupFamiliaCreate(BaseModel):
    familia_origem_id: UUID
    familia_destino_id: UUID
    tempo_setup_minutos: int = Field(gt=0, le=2_147_483_647, strict=True)

    @field_validator("tempo_setup_minutos", mode="before")
    @classmethod
    def validar_tempo_setup(cls, valor: object) -> int:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0 or valor > 2_147_483_647:
            raise ValueError(
                "O tempo de setup informado é inválido. Informe um número inteiro de minutos maior que zero."
            )
        return valor

    @model_validator(mode="after")
    def validar_familias_diferentes(self):
        if self.familia_origem_id == self.familia_destino_id:
            raise ValueError(
                "As famílias de origem e destino devem ser diferentes."
            )
        return self


class FamiliaResumoSetup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str


class TempoSetupFamiliaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_tempo_setup: UUID
    familia_origem: FamiliaResumoSetup
    familia_destino: FamiliaResumoSetup
    tempo_setup_minutos: int
    criado_em: datetime
    atualizado_em: datetime
