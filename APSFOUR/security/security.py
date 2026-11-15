import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "chave_secreta_padrao_para_desenvolvimento_deve_conter_ao_menos_32_bytes_de_tamanho_aps4"
)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

password_hasher = PasswordHash.recommended()
http_bearer_scheme = HTTPBearer(auto_error=False)


def gerar_hash_senha(senha: str) -> str:
    return password_hasher.hash(senha)


def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    return password_hasher.verify(senha_pura, senha_hash)


def criar_token_acesso(dados: dict, delta_expiracao: Optional[timedelta] = None) -> str:
    dados_token = dados.copy()
    agora = datetime.now(timezone.utc)
    if delta_expiracao:
        expira_em = agora + delta_expiracao
    else:
        expira_em = agora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    dados_token.update({
        "exp": expira_em,
        "iat": agora
    })
    token = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decodificar_token_acesso(token: str) -> dict:
    try:
        conteudo = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return conteudo
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def obter_usuario_logado(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    if not credenciais or not credenciais.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credenciais.credentials
    dados = decodificar_token_acesso(token)

    usuario_id = dados.get("usuario_id")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def exigir_perfis(perfis_autorizados: List[str]):
    def verificador_perfil(usuario: Usuario = Depends(obter_usuario_logado)) -> Usuario:
        if usuario.perfil not in perfis_autorizados:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para executar esta operação."
            )
        return usuario
    return verificador_perfil


exigir_administrador = exigir_perfis(["administrador"])
exigir_autenticado = exigir_perfis(["administrador", "usuario"])
