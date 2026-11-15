from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.evento_schema import EventoCreate, EventoResponse, EventoUpdate
from security.security import exigir_administrador, exigir_autenticado
from service import evento_service

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo evento academico (Acesso Restrito: Administrador)"
)
def criar_evento(
    dados: EventoCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return evento_service.criar_evento(db, dados)


@router.get(
    "",
    response_model=List[EventoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os eventos disponiveis (Requer Autenticacao)"
)
def listar_eventos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return evento_service.listar_eventos(db, categoria)


@router.get(
    "/{evento_id}",
    response_model=EventoResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca detalhes de um evento por identificador (Requer Autenticacao)"
)
def obter_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(exigir_autenticado)
):
    return evento_service.obter_evento_por_id(db, evento_id)


@router.put(
    "/{evento_id}",
    response_model=EventoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza dados de um evento (Acesso Restrito: Administrador)"
)
def atualizar_evento(
    evento_id: int,
    dados: EventoUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return evento_service.atualizar_evento(db, evento_id, dados)


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_200_OK,
    summary="Exclui um evento (Acesso Restrito: Administrador)"
)
def excluir_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return evento_service.excluir_evento(db, evento_id)
