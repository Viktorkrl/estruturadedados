from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.participante_schema import (
    ParticipanteCreate,
    ParticipanteResponse,
    ParticipanteUpdate,
)
from security.security import exigir_administrador, exigir_autenticado
from service import participante_service

router = APIRouter(prefix="/participantes", tags=["Participantes"])


@router.post(
    "",
    response_model=ParticipanteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo participante (Requer Autenticacao)"
)
def criar_participante(
    dados: ParticipanteCreate,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return participante_service.criar_participante(db, dados)


@router.get(
    "",
    response_model=List[ParticipanteResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os participantes cadastrados (Requer Autenticacao)"
)
def listar_participantes(
    curso: Optional[str] = Query(None, description="Filtrar por curso"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return participante_service.listar_participantes(db, curso)


@router.get(
    "/{participante_id}",
    response_model=ParticipanteResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca dados de um participante por identificador (Requer Autenticacao)"
)
def obter_participante(
    participante_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return participante_service.obter_participante_por_id(db, participante_id)


@router.put(
    "/{participante_id}",
    response_model=ParticipanteResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza dados do participante (Acesso Restrito: Administrador)"
)
def atualizar_participante(
    participante_id: int,
    dados: ParticipanteUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return participante_service.atualizar_participante(db, participante_id, dados)


@router.delete(
    "/{participante_id}",
    status_code=status.HTTP_200_OK,
    summary="Exclui um participante (Acesso Restrito: Administrador)"
)
def excluir_participante(
    participante_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return participante_service.excluir_participante(db, participante_id)
