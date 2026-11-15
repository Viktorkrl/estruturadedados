from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.usuario_schema import UsuarioCreate, UsuarioResponse
from security.security import exigir_administrador
from service import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo usuario no sistema"
)
def cadastrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.criar_usuario(db, dados)


@router.get(
    "",
    response_model=List[UsuarioResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os usuarios cadastrados (Acesso Restrito: Administrador)"
)
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return usuario_service.listar_usuarios(db)
