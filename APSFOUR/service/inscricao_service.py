from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.evento import Evento
from model.inscricao import Inscricao
from model.participante import Participante
from schema.inscricao_schema import InscricaoCreate, InscricaoResponse


def montar_inscricao_response(inscricao: Inscricao) -> InscricaoResponse:
    return InscricaoResponse(
        id=inscricao.id,
        evento_id=inscricao.evento_id,
        participante_id=inscricao.participante_id,
        data_inscricao=inscricao.data_inscricao,
        evento_nome=inscricao.evento.nome if inscricao.evento else None,
        participante_nome=inscricao.participante.nome if inscricao.participante else None,
    )


def criar_inscricao(db: Session, dados: InscricaoCreate) -> InscricaoResponse:
    evento = db.query(Evento).filter(Evento.id == dados.evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado."
        )

    participante = db.query(Participante).filter(Participante.id == dados.participante_id).first()
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante não encontrado."
        )

    duplicada = (
        db.query(Inscricao)
        .filter(
            Inscricao.evento_id == dados.evento_id,
            Inscricao.participante_id == dados.participante_id
        )
        .first()
    )
    if duplicada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Participante já inscrito neste evento."
        )

    total_inscritos = db.query(Inscricao).filter(Inscricao.evento_id == dados.evento_id).count()
    if total_inscritos >= evento.vagas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evento com vagas esgotadas."
        )

    nova_inscricao = Inscricao(
        evento_id=dados.evento_id,
        participante_id=dados.participante_id
    )
    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)

    return montar_inscricao_response(nova_inscricao)


def listar_inscricoes(
    db: Session,
    evento_id: Optional[int] = None,
    participante_id: Optional[int] = None
) -> List[InscricaoResponse]:
    consulta = db.query(Inscricao)
    if evento_id:
        consulta = consulta.filter(Inscricao.evento_id == evento_id)
    if participante_id:
        consulta = consulta.filter(Inscricao.participante_id == participante_id)

    inscricoes = consulta.order_by(Inscricao.id.asc()).all()
    return [montar_inscricao_response(i) for i in inscricoes]


def obter_inscricao_por_id(db: Session, inscricao_id: int) -> InscricaoResponse:
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscrição não encontrada."
        )
    return montar_inscricao_response(inscricao)


def cancelar_inscricao(db: Session, inscricao_id: int) -> dict:
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inscrição não encontrada."
        )
    db.delete(inscricao)
    db.commit()
    return {"mensagem": "Inscrição cancelada com sucesso."}
