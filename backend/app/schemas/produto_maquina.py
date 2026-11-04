
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.maquina import MaquinaResponse


class ProdutoMaquinasUpdate(BaseModel):
    maquinas_ids: list[UUID] = Field(default_factory=list)


class ProdutoMaquinasResponse(BaseModel):
    id_produto: UUID
    maquinas_compativeis: list[MaquinaResponse]
    possui_maquina_compativel: bool
