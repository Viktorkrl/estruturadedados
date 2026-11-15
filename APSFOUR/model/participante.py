from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    curso = Column(String(100), nullable=False, index=True)

    inscricoes = relationship(
        "Inscricao",
        back_populates="participante",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
