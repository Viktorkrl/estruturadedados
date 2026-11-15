from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class ParticipanteCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do participante")
    email: EmailStr = Field(..., description="E-mail do participante")
    curso: str = Field(..., min_length=2, max_length=100, description="Curso do participante")

    @field_validator("nome", "curso")
    @classmethod
    def validar_campos_texto(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("O campo nao pode ser vazio ou composto apenas por espacos.")
        return trimmed


class ParticipanteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    curso: Optional[str] = Field(None, min_length=2, max_length=100)


class ParticipanteResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    curso: str

    model_config = {"from_attributes": True}
