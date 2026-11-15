from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.inscricao_schema import InscricaoCreate, InscricaoResponse
from security.security import exigir_administrador, exigir_autenticado
from service import inscricao_service

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])


@router.post(
    "",
    response_model=InscricaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realiza a inscricao de um participante em um evento (Requer Autenticacao)"
)
def criar_inscricao(
    dados: InscricaoCreate,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return inscricao_service.criar_inscricao(db, dados)


@router.get(
    "",
    response_model=List[InscricaoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista inscricoes realizadas (Requer Autenticacao)"
)
def listar_inscricoes(
    evento_id: Optional[int] = Query(None, description="Filtrar por evento"),
    participante_id: Optional[int] = Query(None, description="Filtrar por participante"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return inscricao_service.listar_inscricoes(db, evento_id, participante_id)


@router.get(
    "/{inscricao_id}",
    response_model=InscricaoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta uma inscricao especifica (Requer Autenticacao)"
)
def obter_inscricao(
    inscricao_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return inscricao_service.obter_inscricao_por_id(db, inscricao_id)


@router.delete(
    "/{inscricao_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancela uma inscricao (Acesso Restrito: Administrador)"
)
def cancelar_inscricao(
    inscricao_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return inscricao_service.cancelar_inscricao(db, inscricao_id)
