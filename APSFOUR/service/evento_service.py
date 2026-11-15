from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.evento import Evento
from model.inscricao import Inscricao
from schema.evento_schema import EventoCreate, EventoResponse, EventoUpdate


def montar_evento_response(evento: Evento, db: Session) -> EventoResponse:
    total_inscritos = db.query(Inscricao).filter(Inscricao.evento_id == evento.id).count()
    vagas_disponiveis = max(0, evento.vagas - total_inscritos)
    return EventoResponse(
        id=evento.id,
        nome=evento.nome,
        descricao=evento.descricao,
        categoria=evento.categoria,
        data_evento=evento.data_evento,
        vagas=evento.vagas,
        vagas_ocupadas=total_inscritos,
        vagas_disponiveis=vagas_disponiveis
    )


def criar_evento(db: Session, dados: EventoCreate) -> EventoResponse:
    novo_evento = Evento(
        nome=dados.nome.strip(),
        descricao=dados.descricao.strip() if dados.descricao else None,
        categoria=dados.categoria.strip(),
        data_evento=dados.data_evento.strip(),
        vagas=dados.vagas
    )
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return montar_evento_response(novo_evento, db)


def listar_eventos(db: Session, categoria: Optional[str] = None) -> List[EventoResponse]:
    consulta = db.query(Evento)
    if categoria:
        consulta = consulta.filter(Evento.categoria.ilike(f"%{categoria.strip()}%"))
    eventos = consulta.order_by(Evento.id.asc()).all()
    return [montar_evento_response(ev, db) for ev in eventos]


def obter_evento_por_id(db: Session, evento_id: int) -> EventoResponse:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado."
        )
    return montar_evento_response(evento, db)


def atualizar_evento(db: Session, evento_id: int, dados: EventoUpdate) -> EventoResponse:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado."
        )

    total_inscritos = db.query(Inscricao).filter(Inscricao.evento_id == evento.id).count()

    if dados.vagas is not None:
        if dados.vagas < total_inscritos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível reduzir as vagas para {dados.vagas}, pois já existem {total_inscritos} inscrições ativas."
            )
        evento.vagas = dados.vagas

    if dados.nome is not None:
        evento.nome = dados.nome.strip()
    if dados.descricao is not None:
        evento.descricao = dados.descricao.strip() if dados.descricao else None
    if dados.categoria is not None:
        evento.categoria = dados.categoria.strip()
    if dados.data_evento is not None:
        evento.data_evento = dados.data_evento.strip()

    db.commit()
    db.refresh(evento)
    return montar_evento_response(evento, db)


def excluir_evento(db: Session, evento_id: int) -> dict:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado."
        )
    db.delete(evento)
    db.commit()
    return {"mensagem": "Evento removido com sucesso."}
