from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EventoCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, description="Nome do evento")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descricao detalhada")
    categoria: str = Field(..., min_length=2, max_length=80, description="Categoria do evento")
    data_evento: str = Field(..., min_length=4, max_length=30, description="Data do evento")
    vagas: int = Field(..., gt=0, description="Quantidade total de vagas disponiveis")

    @field_validator("nome", "categoria", "data_evento")
    @classmethod
    def validar_campos_texto(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("O campo nao pode ser vazio ou composto apenas por espacos.")
        return trimmed


class EventoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    descricao: Optional[str] = Field(None, max_length=1000)
    categoria: Optional[str] = Field(None, min_length=2, max_length=80)
    data_evento: Optional[str] = Field(None, min_length=4, max_length=30)
    vagas: Optional[int] = Field(None, gt=0)


class EventoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    categoria: str
    data_evento: str
    vagas: int
    vagas_ocupadas: int = 0
    vagas_disponiveis: int = 0

    model_config = {"from_attributes": True}
