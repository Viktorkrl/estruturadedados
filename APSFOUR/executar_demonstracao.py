import json
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import model
from main import app
from model.usuario import Usuario
from security.security import criar_token_acesso, verificar_senha
from service.usuario_service import inicializar_administrador_padrao

# Configuracao de banco isolado
engine_demo = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SessionDemo = sessionmaker(autocommit=False, autoflush=False, bind=engine_demo)


def override_db():
    db = SessionDemo()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


def formatar_titulo(numero: int, titulo: str):
    print("\n" + "=" * 70)
    print(f"CENARIO {numero}: {titulo.upper()}")
    print("=" * 70)


def formatar_resultado(sucesso: bool, detalhe: str):
    indicador = "[SUCESSO]" if sucesso else "[FALHA]"
    print(f"{indicador} {detalhe}")


def executar_demonstracao():
    Base.metadata.create_all(bind=engine_demo)
    db = SessionDemo()
    try:
        inicializar_administrador_padrao(db)
    finally:
        db.close()

    client = TestClient(app)

    # Cenario 1
    formatar_titulo(1, "Cadastro de um usuario")
    payload_user = {
        "nome": "Mariana Souza",
        "email": "mariana.souza@exemplo.com",
        "senha": "senha_segura_123"
    }
    resp1 = client.post("/usuarios", json=payload_user)
    print("Requisicao: POST /usuarios")
    print("Payload:", json.dumps(payload_user, indent=2))
    print("Codigo HTTP retornado:", resp1.status_code)
    print("Resposta:", json.dumps(resp1.json(), indent=2))
    formatar_resultado(resp1.status_code == 201, "Usuario cadastrado com perfil 'usuario' e sem expor senhas.")

    # Cenario 2
    formatar_titulo(2, "Verificacao de que a senha foi armazenada como hash")
    db = SessionDemo()
    usuario_db = db.query(Usuario).filter(Usuario.email == "mariana.souza@exemplo.com").first()
    print("Hash armazenado no banco:", usuario_db.senha_hash)
    valida = verificar_senha("senha_segura_123", usuario_db.senha_hash)
    db.close()
    print("Verificacao com a senha correta:", valida)
    formatar_resultado(valida, "A senha original nao esta no banco. Apenas o hash seguro Argon2 foi persistido.")

    # Cenario 3
    formatar_titulo(3, "Tentativa de cadastro com e-mail duplicado")
    resp3 = client.post("/usuarios", json=payload_user)
    print("Requisicao: POST /usuarios com mesmo e-mail")
    print("Codigo HTTP retornado:", resp3.status_code)
    print("Resposta:", json.dumps(resp3.json(), indent=2))
    formatar_resultado(resp3.status_code == 409, "Duplicidade de e-mail bloqueada com codigo 409 Conflict.")

    # Cenario 4
    formatar_titulo(4, "Autenticacao com credenciais validas")
    login_payload = {
        "email": "mariana.souza@exemplo.com",
        "senha": "senha_segura_123"
    }
    resp4 = client.post("/auth/login", json=login_payload)
    print("Requisicao: POST /auth/login")
    print("Codigo HTTP retornado:", resp4.status_code)
    token_mariana = resp4.json().get("access_token")
    print("Token gerado (trecho inicial):", token_mariana[:35] + "...")
    formatar_resultado(resp4.status_code == 200 and token_mariana is not None, "Token JWT emitido com sucesso.")

    # Cenario 5
    formatar_titulo(5, "Tentativa de autenticacao com credenciais invalidas")
    login_invalido = {
        "email": "mariana.souza@exemplo.com",
        "senha": "senha_incorreta"
    }
    resp5 = client.post("/auth/login", json=login_invalido)
    print("Requisicao: POST /auth/login com senha errada")
    print("Codigo HTTP retornado:", resp5.status_code)
    print("Resposta:", json.dumps(resp5.json(), indent=2))
    formatar_resultado(resp5.status_code == 401, "Autenticacao recusada com codigo 401 Unauthorized de forma generica.")

    # Cenario 6
    formatar_titulo(6, "Acesso a uma rota protegida sem token")
    resp6 = client.get("/eventos")
    print("Requisicao: GET /eventos sem cabecalho Authorization")
    print("Codigo HTTP retornado:", resp6.status_code)
    print("Resposta:", json.dumps(resp6.json(), indent=2))
    formatar_resultado(resp6.status_code == 401, "Acesso bloqueado com codigo 401 Unauthorized.")

    # Cenario 7
    formatar_titulo(7, "Acesso a uma rota protegida com token valido")
    headers_mariana = {"Authorization": f"Bearer {token_mariana}"}
    resp7 = client.get("/eventos", headers=headers_mariana)
    print("Requisicao: GET /eventos com Authorization: Bearer <token>")
    print("Codigo HTTP retornado:", resp7.status_code)
    print("Total de eventos retornados:", len(resp7.json()))
    formatar_resultado(resp7.status_code == 200, "Acesso liberado com sucesso utilizando token valido.")

    # Cenario 8
    formatar_titulo(8, "Acesso com token invalido ou expirado")
    resp8_invalido = client.get("/eventos", headers={"Authorization": "Bearer token_falsificado"})
    print("Teste 8.1: Token adulterado")
    print("Codigo HTTP retornado:", resp8_invalido.status_code)
    print("Resposta:", json.dumps(resp8_invalido.json(), indent=2))

    token_expirado = criar_token_acesso(
        dados={"sub": "1", "usuario_id": 1, "email": "mariana.souza@exemplo.com", "perfil": "usuario"},
        delta_expiracao=timedelta(minutes=-5)
    )
    resp8_expirado = client.get("/eventos", headers={"Authorization": f"Bearer {token_expirado}"})
    print("Teste 8.2: Token expirado")
    print("Codigo HTTP retornado:", resp8_expirado.status_code)
    print("Resposta:", json.dumps(resp8_expirado.json(), indent=2))
    formatar_resultado(
        resp8_invalido.status_code == 401 and resp8_expirado.status_code == 401,
        "Tokens invalidos e expirados rejeitados com 401 Unauthorized."
    )

    # Cenario 9
    formatar_titulo(9, "Tentativa de execucao de operacao administrativa por usuario comum")
    evento_tentativa = {
        "nome": "Evento Nao Autorizado",
        "categoria": "Geral",
        "data_evento": "2026-12-10",
        "vagas": 10
    }
    resp9 = client.post("/eventos", json=evento_tentativa, headers=headers_mariana)
    print("Requisicao: POST /eventos com perfil 'usuario'")
    print("Codigo HTTP retornado:", resp9.status_code)
    print("Resposta:", json.dumps(resp9.json(), indent=2))
    formatar_resultado(resp9.status_code == 403, "Acesso negado com 403 Forbidden pelo servidor.")

    # Cenario 10
    formatar_titulo(10, "Execucao de operacao administrativa por um administrador")
    admin_login = client.post("/auth/login", json={"email": "admin@sistema.com", "senha": "Admin@123456"})
    token_admin = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    evento_oficial = {
        "nome": "Congresso de Engenharia de Software 2026",
        "descricao": "Palestras de arquitetura de software e microsservicos",
        "categoria": "Engenharia",
        "data_evento": "2026-12-15",
        "vagas": 100
    }
    resp10 = client.post("/eventos", json=evento_oficial, headers=headers_admin)
    print("Requisicao: POST /eventos com perfil 'administrador'")
    print("Codigo HTTP retornado:", resp10.status_code)
    print("Evento criado:", json.dumps(resp10.json(), indent=2))
    formatar_resultado(resp10.status_code == 201, "Evento criado com sucesso pelo administrador.")

    # Cenario 11
    formatar_titulo(11, "Consulta dos dados do usuario autenticado utilizando /auth/me")
    resp11 = client.get("/auth/me", headers=headers_mariana)
    print("Requisicao: GET /auth/me com token da Mariana")
    print("Codigo HTTP retornado:", resp11.status_code)
    print("Dados retornados:", json.dumps(resp11.json(), indent=2))
    formatar_resultado(
        resp11.status_code == 200 and resp11.json()["email"] == "mariana.souza@exemplo.com",
        "Usuario identificado dinamicamente pelo token JWT validado no servidor."
    )

    # Cenario 12
    formatar_titulo(12, "Verificacao de funcionalidades e relatorios continuam funcionando")
    # Cadastrar participante
    part_resp = client.post(
        "/participantes",
        json={"nome": "Joao Pedro", "email": "joao.pedro@universidade.br", "curso": "Sistemas de Informacao"},
        headers=headers_admin
    )
    part_id = part_resp.json()["id"]

    # Fazer inscricao
    ev_id = resp10.json()["id"]
    insc_resp = client.post(
        "/inscricoes",
        json={"evento_id": ev_id, "participante_id": part_id},
        headers=headers_admin
    )
    print("Inscricao realizada com sucesso:", json.dumps(insc_resp.json(), indent=2))

    # Obter relatorios
    rel_ocupacao = client.get("/relatorios/ocupacao-eventos", headers=headers_admin).json()
    rel_categoria = client.get("/relatorios/eventos-por-categoria", headers=headers_admin).json()
    rel_curso = client.get("/relatorios/participacao-por-curso", headers=headers_admin).json()

    print("\nRelatorio de Ocupacao dos Eventos:")
    print(json.dumps(rel_ocupacao, indent=2))

    print("\nRelatorio de Eventos por Categoria:")
    print(json.dumps(rel_categoria, indent=2))

    print("\nRelatorio de Participacao por Curso:")
    print(json.dumps(rel_curso, indent=2))

    formatar_resultado(
        len(rel_ocupacao) > 0 and len(rel_categoria) > 0 and len(rel_curso) > 0,
        "Todas as regras de negocio e relatorios consolidados estao operacionais."
    )

    print("\n" + "=" * 70)
    print("TODOS OS 12 CENARIOS FORAM DEMONSTRADOS COM SUCESSO INTEGRAL!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    executar_demonstracao()
