from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from model.usuario import Usuario
from schema.relatorio_schema import (
    RelatorioCategoriaItem,
    RelatorioCursoItem,
    RelatorioOcupacaoItem,
)
from security.security import exigir_administrador
from service import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["Relatórios Consolidados"])


@router.get(
    "/ocupacao-eventos",
    response_model=List[RelatorioOcupacaoItem],
    status_code=status.HTTP_200_OK,
    summary="Relatorio consolidado de taxa de ocupacao dos eventos (Acesso Restrito: Administrador)"
)
def relatorio_ocupacao(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return relatorio_service.obter_relatorio_ocupacao(db)


@router.get(
    "/eventos-por-categoria",
    response_model=List[RelatorioCategoriaItem],
    status_code=status.HTTP_200_OK,
    summary="Relatorio consolidado de eventos e vagas agrupados por categoria (Acesso Restrito: Administrador)"
)
def relatorio_por_categoria(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return relatorio_service.obter_relatorio_por_categoria(db)


@router.get(
    "/participacao-por-curso",
    response_model=List[RelatorioCursoItem],
    status_code=status.HTTP_200_OK,
    summary="Relatorio consolidado de inscricoes por curso (Acesso Restrito: Administrador)"
)
def relatorio_por_curso(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(exigir_administrador)
):
    return relatorio_service.obter_relatorio_por_curso(db)
