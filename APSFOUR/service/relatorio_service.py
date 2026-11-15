from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from model.evento import Evento
from model.inscricao import Inscricao
from model.participante import Participante
from schema.relatorio_schema import (
    RelatorioCategoriaItem,
    RelatorioCursoItem,
    RelatorioOcupacaoItem,
)


def obter_relatorio_ocupacao(db: Session) -> List[RelatorioOcupacaoItem]:
    eventos = db.query(Evento).order_by(Evento.id.asc()).all()
    resultado: List[RelatorioOcupacaoItem] = []

    for ev in eventos:
        inscritos = db.query(Inscricao).filter(Inscricao.evento_id == ev.id).count()
        restantes = max(0, ev.vagas - inscritos)
        taxa = round((inscritos / ev.vagas) * 100, 2) if ev.vagas > 0 else 0.0

        if inscritos >= ev.vagas:
            status_lotacao = "Esgotado"
        elif taxa >= 80.0:
            status_lotacao = "Alta Ocupacao"
        elif taxa >= 50.0:
            status_lotacao = "Media Ocupacao"
        else:
            status_lotacao = "Vagas Disponiveis"

        resultado.append(
            RelatorioOcupacaoItem(
                evento_id=ev.id,
                nome=ev.nome,
                categoria=ev.categoria,
                vagas_totais=ev.vagas,
                vagas_preenchidas=inscritos,
                vagas_restantes=restantes,
                taxa_ocupacao_percentual=taxa,
                status_lotacao=status_lotacao
            )
        )

    return resultado


def obter_relatorio_por_categoria(db: Session) -> List[RelatorioCategoriaItem]:
    categorias_distintas = (
        db.query(Evento.categoria)
        .distinct()
        .order_by(Evento.categoria.asc())
        .all()
    )

    resultado: List[RelatorioCategoriaItem] = []
    for (categoria,) in categorias_distintas:
        eventos_cat = db.query(Evento).filter(Evento.categoria == categoria).all()
        ids_eventos = [ev.id for ev in eventos_cat]
        total_vagas = sum(ev.vagas for ev in eventos_cat)
        total_inscricoes = (
            db.query(Inscricao)
            .filter(Inscricao.evento_id.in_(ids_eventos))
            .count()
            if ids_eventos else 0
        )

        resultado.append(
            RelatorioCategoriaItem(
                categoria=categoria,
                total_eventos=len(eventos_cat),
                total_vagas=total_vagas,
                total_inscricoes=total_inscricoes
            )
        )

    return resultado


def obter_relatorio_por_curso(db: Session) -> List[RelatorioCursoItem]:
    cursos_distintos = (
        db.query(Participante.curso)
        .distinct()
        .order_by(Participante.curso.asc())
        .all()
    )

    resultado: List[RelatorioCursoItem] = []
    for (curso,) in cursos_distintos:
        participantes_curso = db.query(Participante).filter(Participante.curso == curso).all()
        ids_participantes = [p.id for p in participantes_curso]
        total_inscricoes = (
            db.query(Inscricao)
            .filter(Inscricao.participante_id.in_(ids_participantes))
            .count()
            if ids_participantes else 0
        )

        resultado.append(
            RelatorioCursoItem(
                curso=curso,
                total_participantes=len(participantes_curso),
                total_inscricoes=total_inscricoes
            )
        )

    return resultado
