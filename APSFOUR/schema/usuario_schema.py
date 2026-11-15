from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuario")
    email: EmailStr = Field(..., description="E-mail valido do usuario")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha com no minimo 6 caracteres")

    @field_validator("nome")
    @classmethod
    def validar_nome_nao_vazio(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("O nome nao pode ser vazio ou conter apenas espacos.")
        return trimmed

    @field_validator("senha")
    @classmethod
    def validar_senha_criterios(cls, value: str) -> str:
        if len(value.strip()) < 6:
            raise ValueError("A senha deve conter no minimo 6 caracteres validos.")
        return value


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str

    model_config = {"from_attributes": True}


class UsuarioLogin(BaseModel):
    email: EmailStr = Field(..., description="E-mail cadastrado")
    senha: str = Field(..., min_length=1, description="Senha do usuario")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    usuario_id: int
    email: str
    perfil: str
