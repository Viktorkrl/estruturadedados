from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.usuario import Usuario
from schema.usuario_schema import TokenResponse, UsuarioLogin
from security.security import criar_token_acesso, verificar_senha


def autenticar_usuario(db: Session, credenciais: UsuarioLogin) -> TokenResponse:
    email_normalizado = credenciais.email.lower().strip()
    usuario = db.query(Usuario).filter(Usuario.email == email_normalizado).first()

    if not usuario or not verificar_senha(credenciais.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    dados_token = {
        "sub": str(usuario.id),
        "usuario_id": usuario.id,
        "email": usuario.email,
        "perfil": usuario.perfil
    }
    token = criar_token_acesso(dados=dados_token)

    return TokenResponse(access_token=token, token_type="bearer")
