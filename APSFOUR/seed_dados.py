import os
from database import Base, SessionLocal, engine
from model.evento import Evento
from model.inscricao import Inscricao
from model.participante import Participante
from model.usuario import Usuario
from security.security import gerar_hash_senha


def popular_dados_iniciais():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Administrador padrao
        admin = db.query(Usuario).filter(Usuario.email == "admin@sistema.com").first()
        if not admin:
            admin = Usuario(
                nome="Administrador Geral",
                email="admin@sistema.com",
                senha_hash=gerar_hash_senha("Admin@123456"),
                perfil="administrador"
            )
            db.add(admin)

        # Usuario comum para testes
        usuario = db.query(Usuario).filter(Usuario.email == "aluno@exemplo.com").first()
        if not usuario:
            usuario = Usuario(
                nome="Aluno Exemplo",
                email="aluno@exemplo.com",
                senha_hash=gerar_hash_senha("senha_segura"),
                perfil="usuario"
            )
            db.add(usuario)

        db.commit()

        # Eventos academicos
        if db.query(Evento).count() == 0:
            ev1 = Evento(
                nome="Semana Academica de Tecnologia",
                descricao="Ciclo de palestras e oficinas sobre desenvolvimento de software e nuvem",
                categoria="Tecnologia",
                data_evento="2026-11-20",
                vagas=50
            )
            ev2 = Evento(
                nome="Congresso de Inovacao e Inteligencia Artificial",
                descricao="Encontro anual sobre avancos em IA aplicada e automacao",
                categoria="Tecnologia",
                data_evento="2026-11-25",
                vagas=2
            )
            ev3 = Evento(
                nome="Simposio de Gestao e Lideranca",
                descricao="Debates sobre gestao estrategica e lideranca em organizacoes",
                categoria="Gestao",
                data_evento="2026-12-05",
                vagas=30
            )
            db.add_all([ev1, ev2, ev3])
            db.commit()

        # Participantes
        if db.query(Participante).count() == 0:
            p1 = Participante(
                nome="Lucas Mendes",
                email="lucas.mendes@universidade.br",
                curso="Engenharia de Software"
            )
            p2 = Participante(
                nome="Beatriz Santos",
                email="beatriz.santos@universidade.br",
                curso="Engenharia de Software"
            )
            p3 = Participante(
                nome="Carlos Eduardo",
                email="carlos.eduardo@universidade.br",
                curso="Administracao"
            )
            p4 = Participante(
                nome="Mariana Lima",
                email="mariana.lima@universidade.br",
                curso="Direito"
            )
            db.add_all([p1, p2, p3, p4])
            db.commit()

        # Inscricoes
        if db.query(Inscricao).count() == 0:
            ev1 = db.query(Evento).filter(Evento.nome.like("%Semana Academica%")).first()
            ev2 = db.query(Evento).filter(Evento.nome.like("%Congresso de Inovacao%")).first()
            p1 = db.query(Participante).filter(Participante.email == "lucas.mendes@universidade.br").first()
            p2 = db.query(Participante).filter(Participante.email == "beatriz.santos@universidade.br").first()
            p3 = db.query(Participante).filter(Participante.email == "carlos.eduardo@universidade.br").first()

            if ev1 and p1:
                db.add(Inscricao(evento_id=ev1.id, participante_id=p1.id))
            if ev1 and p2:
                db.add(Inscricao(evento_id=ev1.id, participante_id=p2.id))
            if ev2 and p1:
                db.add(Inscricao(evento_id=ev2.id, participante_id=p1.id))
            if ev2 and p2:
                db.add(Inscricao(evento_id=ev2.id, participante_id=p2.id))

            db.commit()

        print("Carga inicial de dados executada com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    popular_dados_iniciais()
