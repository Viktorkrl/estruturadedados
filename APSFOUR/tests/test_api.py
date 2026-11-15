import os
from datetime import timedelta
import pytest
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

# Banco de dados isolado com StaticPool para compartilhar memoria entre sessoes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        inicializar_administrador_padrao(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


# Cenario 1: Cadastro de um usuario
def test_01_cadastro_usuario(client: TestClient):
    payload = {
        "nome": "Carlos Silva",
        "email": "carlos.silva@exemplo.com",
        "senha": "senha_secreta_123"
    }
    response = client.post("/usuarios", json=payload)
    assert response.status_code == 201
    dados = response.json()
    assert dados["id"] is not None
    assert dados["nome"] == "Carlos Silva"
    assert dados["email"] == "carlos.silva@exemplo.com"
    assert dados["perfil"] == "usuario"
    assert "senha" not in dados
    assert "senha_hash" not in dados


# Cenario 2: Verificacao de que a senha foi armazenada como hash
def test_02_verificacao_senha_armazenada_como_hash():
    db = TestingSessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == "carlos.silva@exemplo.com").first()
        assert usuario is not None
        assert usuario.senha_hash != "senha_secreta_123"
        assert usuario.senha_hash.startswith("$argon2") or len(usuario.senha_hash) > 30
        assert verificar_senha("senha_secreta_123", usuario.senha_hash) is True
        assert verificar_senha("senha_errada", usuario.senha_hash) is False
    finally:
        db.close()


# Cenario 3: Tentativa de cadastro com e-mail duplicado
def test_03_tentativa_cadastro_email_duplicado(client: TestClient):
    payload = {
        "nome": "Carlos Duplicado",
        "email": "carlos.silva@exemplo.com",
        "senha": "outra_senha_qualquer"
    }
    response = client.post("/usuarios", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Já existe um usuário cadastrado com este e-mail."


# Cenario 4: Autenticacao com credenciais validas
def test_04_autenticacao_credenciais_validas(client: TestClient):
    payload = {
        "email": "carlos.silva@exemplo.com",
        "senha": "senha_secreta_123"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    dados = response.json()
    assert "access_token" in dados
    assert dados["token_type"] == "bearer"
    assert len(dados["access_token"]) > 20


# Cenario 5: Tentativa de autenticacao com credenciais invalidas
def test_05_tentativa_autenticacao_credenciais_invalidas(client: TestClient):
    # Senha incorreta
    resp_senha_errada = client.post(
        "/auth/login",
        json={"email": "carlos.silva@exemplo.com", "senha": "senha_completamente_errada"}
    )
    assert resp_senha_errada.status_code == 401
    assert resp_senha_errada.json()["detail"] == "E-mail ou senha inválidos."

    # Email inexistente
    resp_email_inexistente = client.post(
        "/auth/login",
        json={"email": "inexistente@exemplo.com", "senha": "senha_qualquer"}
    )
    assert resp_email_inexistente.status_code == 401
    assert resp_email_inexistente.json()["detail"] == "E-mail ou senha inválidos."


# Cenario 6: Acesso a uma rota protegida sem token
def test_06_acesso_rota_protegida_sem_token(client: TestClient):
    response = client.get("/eventos")
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais."


# Cenario 7: Acesso a uma rota protegida com token valido
def test_07_acesso_rota_protegida_com_token_valido(client: TestClient):
    login_resp = client.post(
        "/auth/login",
        json={"email": "carlos.silva@exemplo.com", "senha": "senha_secreta_123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/eventos", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Cenario 8: Acesso com token invalido ou expirado
def test_08_acesso_com_token_invalido_ou_expirado(client: TestClient):
    # Token adulterado / invalido
    headers_invalido = {"Authorization": "Bearer token_falso_adulterado_invalido"}
    resp_invalido = client.get("/eventos", headers=headers_invalido)
    assert resp_invalido.status_code == 401
    assert resp_invalido.json()["detail"] == "Não foi possível validar as credenciais."

    # Token expirado
    token_expirado = criar_token_acesso(
        dados={"sub": "1", "usuario_id": 1, "email": "carlos.silva@exemplo.com", "perfil": "usuario"},
        delta_expiracao=timedelta(seconds=-10)
    )
    headers_expirado = {"Authorization": f"Bearer {token_expirado}"}
    resp_expirado = client.get("/eventos", headers=headers_expirado)
    assert resp_expirado.status_code == 401
    assert resp_expirado.json()["detail"] == "Não foi possível validar as credenciais."


# Cenario 9: Tentativa de execucao de operacao administrativa por usuario comum (403 Forbidden)
def test_09_operacao_administrativa_por_usuario_comum(client: TestClient):
    login_resp = client.post(
        "/auth/login",
        json={"email": "carlos.silva@exemplo.com", "senha": "senha_secreta_123"}
    )
    token_usuario = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token_usuario}"}

    novo_evento_payload = {
        "nome": "Hackathon Academico Proibido",
        "descricao": "Tentativa de criacao por usuario sem privilegios",
        "categoria": "Competicao",
        "data_evento": "2026-12-01",
        "vagas": 20
    }
    response = client.post("/eventos", json=novo_evento_payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Você não possui permissão para executar esta operação."

    # Tentativa de acessar relatorios consolidados
    resp_relatorio = client.get("/relatorios/ocupacao-eventos", headers=headers)
    assert resp_relatorio.status_code == 403
    assert resp_relatorio.json()["detail"] == "Você não possui permissão para executar esta operação."


# Cenario 10: Execucao de uma operacao administrativa por um administrador
def test_10_operacao_administrativa_por_administrador(client: TestClient):
    # Login como administrador padrao
    admin_login = client.post(
        "/auth/login",
        json={"email": "admin@sistema.com", "senha": "Admin@123456"}
    )
    assert admin_login.status_code == 200
    token_admin = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Criar evento com permissao de administrador
    evento_payload = {
        "nome": "Semana de Inteligencia Artificial",
        "descricao": "Evento oficial autorizado",
        "categoria": "Tecnologia",
        "data_evento": "2026-11-28",
        "vagas": 40
    }
    resp_criar = client.post("/eventos", json=evento_payload, headers=headers_admin)
    assert resp_criar.status_code == 201
    dados_evento = resp_criar.json()
    assert dados_evento["id"] is not None
    assert dados_evento["nome"] == "Semana de Inteligencia Artificial"

    # Atualizar evento com permissao de administrador
    evento_id = dados_evento["id"]
    resp_atualizar = client.put(
        f"/eventos/{evento_id}",
        json={"vagas": 45, "categoria": "Tecnologia e Inovacao"},
        headers=headers_admin
    )
    assert resp_atualizar.status_code == 200
    assert resp_atualizar.json()["vagas"] == 45


# Cenario 11: Consulta dos dados do usuario autenticado utilizando /auth/me
def test_11_consulta_dados_usuario_autenticado_auth_me(client: TestClient):
    login_resp = client.post(
        "/auth/login",
        json={"email": "carlos.silva@exemplo.com", "senha": "senha_secreta_123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    dados = response.json()
    assert dados["email"] == "carlos.silva@exemplo.com"
    assert dados["nome"] == "Carlos Silva"
    assert dados["perfil"] == "usuario"
    assert "senha" not in dados
    assert "senha_hash" not in dados


# Cenario 12: Verificacao de que as funcionalidades e relatorios continuam funcionando
def test_12_funcionalidades_e_relatorios(client: TestClient):
    # Login do administrador
    admin_login = client.post(
        "/auth/login",
        json={"email": "admin@sistema.com", "senha": "Admin@123456"}
    )
    token_admin = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Cadastrar participante
    part_payload = {
        "nome": "Fernanda Souza",
        "email": "fernanda.souza@universidade.br",
        "curso": "Engenharia de Software"
    }
    resp_part = client.post("/participantes", json=part_payload, headers=headers_admin)
    assert resp_part.status_code == 201
    participante_id = resp_part.json()["id"]

    # Obter id de evento existente
    eventos = client.get("/eventos", headers=headers_admin).json()
    assert len(eventos) > 0
    evento_id = eventos[0]["id"]

    # Realizar inscricao
    inscricao_payload = {
        "evento_id": evento_id,
        "participante_id": participante_id
    }
    resp_insc = client.post("/inscricoes", json=inscricao_payload, headers=headers_admin)
    assert resp_insc.status_code == 201
    dados_insc = resp_insc.json()
    assert dados_insc["evento_id"] == evento_id
    assert dados_insc["participante_id"] == participante_id

    # Impedir inscricao duplicada
    resp_duplicada = client.post("/inscricoes", json=inscricao_payload, headers=headers_admin)
    assert resp_duplicada.status_code == 409
    assert resp_duplicada.json()["detail"] == "Participante já inscrito neste evento."

    # Consultar relatorio de ocupacao
    resp_rel_ocupacao = client.get("/relatorios/ocupacao-eventos", headers=headers_admin)
    assert resp_rel_ocupacao.status_code == 200
    assert len(resp_rel_ocupacao.json()) > 0
    assert "taxa_ocupacao_percentual" in resp_rel_ocupacao.json()[0]

    # Consultar relatorio por categoria
    resp_rel_cat = client.get("/relatorios/eventos-por-categoria", headers=headers_admin)
    assert resp_rel_cat.status_code == 200
    assert len(resp_rel_cat.json()) > 0

    # Consultar relatorio por curso
    resp_rel_curso = client.get("/relatorios/participacao-por-curso", headers=headers_admin)
    assert resp_rel_curso.status_code == 200
    assert len(resp_rel_curso.json()) > 0
