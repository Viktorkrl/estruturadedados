from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.usuario_schema import TokenResponse, UsuarioLogin, UsuarioResponse
from security.security import obter_usuario_logado
from service import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Realiza a autenticacao de um usuario e retorna um token JWT"
)
def login(credenciais: UsuarioLogin, db: Session = Depends(get_db)):
    return auth_service.autenticar_usuario(db, credenciais)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta informacoes do usuario associado ao token atual"
)
def consultar_meu_usuario(usuario_atual: Usuario = Depends(obter_usuario_logado)):
    return usuario_atual
