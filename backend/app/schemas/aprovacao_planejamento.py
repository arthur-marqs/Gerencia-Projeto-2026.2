from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AliasPath, BaseModel, ConfigDict, Field

OrigemPlanejamento = Literal["manual", "sugerida"]


class AprovacaoPlanejamentoCreate(BaseModel):
    origem: OrigemPlanejamento | None = None
    origem_id: UUID | None = None
    ordens_ids: list[UUID] | None = None


class ItemAprovacaoPlanejamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ordem_id: UUID
    codigo_ordem: str = Field(validation_alias=AliasPath("ordem", "codigo"))
    posicao: int
    maquina_id: UUID | None = None
    codigo_maquina: str | None = Field(default=None, validation_alias=AliasPath("maquina", "codigo"))


class SequenciaParaAprovacaoResponse(BaseModel):
    origem: OrigemPlanejamento
    origem_id: UUID
    nome: str
    itens: list[ItemAprovacaoPlanejamentoResponse]


class CandidatoAprovacaoResponse(SequenciaParaAprovacaoResponse):
    criado_em: datetime


class AprovacaoPlanejamentoResponse(SequenciaParaAprovacaoResponse):
    id_aprovacao: UUID
    status: Literal["APROVADO"] = "APROVADO"
    aprovado_por: UUID
    aprovado_em: datetime
