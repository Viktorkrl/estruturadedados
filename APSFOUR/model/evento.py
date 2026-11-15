from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    categoria = Column(String(80), nullable=False, index=True)
    data_evento = Column(String(30), nullable=False)
    vagas = Column(Integer, nullable=False)

    inscricoes = relationship(
        "Inscricao",
        back_populates="evento",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
