import os
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.usuario import Usuario
from schema.usuario_schema import UsuarioCreate
from security.security import gerar_hash_senha


def criar_usuario(db: Session, dados: UsuarioCreate) -> Usuario:
    email_normalizado = dados.email.lower().strip()
    usuario_existente = db.query(Usuario).filter(Usuario.email == email_normalizado).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este e-mail."
        )

    senha_criptografada = gerar_hash_senha(dados.senha)

    novo_usuario = Usuario(
        nome=dados.nome.strip(),
        email=email_normalizado,
        senha_hash=senha_criptografada,
        perfil="usuario"
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def obter_usuario_por_id(db: Session, usuario_id: int) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
    return usuario


def obter_usuario_por_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email.lower().strip()).first()


def listar_usuarios(db: Session) -> List[Usuario]:
    return db.query(Usuario).all()


def inicializar_administrador_padrao(db: Session) -> Optional[Usuario]:
    admin_existente = db.query(Usuario).filter(Usuario.perfil == "administrador").first()
    if admin_existente:
        return admin_existente

    nome_admin = os.getenv("DEFAULT_ADMIN_NAME", "Administrador Inicial")
    email_admin = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@sistema.com").lower().strip()
    senha_admin = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123456")

    usuario_mesmo_email = db.query(Usuario).filter(Usuario.email == email_admin).first()
    if usuario_mesmo_email:
        usuario_mesmo_email.perfil = "administrador"
        db.commit()
        db.refresh(usuario_mesmo_email)
        return usuario_mesmo_email

    novo_admin = Usuario(
        nome=nome_admin,
        email=email_admin,
        senha_hash=gerar_hash_senha(senha_admin),
        perfil="administrador"
    )
    db.add(novo_admin)
    db.commit()
    db.refresh(novo_admin)
    return novo_admin
