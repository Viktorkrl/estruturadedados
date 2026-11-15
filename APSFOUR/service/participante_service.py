from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.participante import Participante
from schema.participante_schema import (
    ParticipanteCreate,
    ParticipanteResponse,
    ParticipanteUpdate,
)


def criar_participante(db: Session, dados: ParticipanteCreate) -> Participante:
    email_normalizado = dados.email.lower().strip()
    existente = db.query(Participante).filter(Participante.email == email_normalizado).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um participante cadastrado com este e-mail."
        )

    novo_participante = Participante(
        nome=dados.nome.strip(),
        email=email_normalizado,
        curso=dados.curso.strip()
    )
    db.add(novo_participante)
    db.commit()
    db.refresh(novo_participante)
    return novo_participante


def listar_participantes(db: Session, curso: Optional[str] = None) -> List[Participante]:
    consulta = db.query(Participante)
    if curso:
        consulta = consulta.filter(Participante.curso.ilike(f"%{curso.strip()}%"))
    return consulta.order_by(Participante.id.asc()).all()


def obter_participante_por_id(db: Session, participante_id: int) -> Participante:
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante não encontrado."
        )
    return participante


def atualizar_participante(
    db: Session,
    participante_id: int,
    dados: ParticipanteUpdate
) -> Participante:
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante não encontrado."
        )

    if dados.email is not None:
        email_normalizado = dados.email.lower().strip()
        outro = (
            db.query(Participante)
            .filter(Participante.email == email_normalizado, Participante.id != participante_id)
            .first()
        )
        if outro:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um participante cadastrado com este e-mail."
            )
        participante.email = email_normalizado

    if dados.nome is not None:
        participante.nome = dados.nome.strip()
    if dados.curso is not None:
        participante.curso = dados.curso.strip()

    db.commit()
    db.refresh(participante)
    return participante


def excluir_participante(db: Session, participante_id: int) -> dict:
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante não encontrado."
        )
    db.delete(participante)
    db.commit()
    return {"mensagem": "Participante removido com sucesso."}
