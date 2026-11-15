from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InscricaoCreate(BaseModel):
    evento_id: int = Field(..., gt=0, description="Identificador do evento")
    participante_id: int = Field(..., gt=0, description="Identificador do participante")


class InscricaoResponse(BaseModel):
    id: int
    evento_id: int
    participante_id: int
    data_inscricao: datetime
    evento_nome: Optional[str] = None
    participante_nome: Optional[str] = None

    model_config = {"from_attributes": True}
