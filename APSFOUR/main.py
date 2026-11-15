from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from database import Base, SessionLocal, engine
import model
from controller import (
    auth_router,
    evento_router,
    inscricao_router,
    participante_router,
    relatorio_router,
    usuario_router,
)
from service.usuario_service import inicializar_administrador_padrao


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inicializar_administrador_padrao(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="API de Gestão de Eventos Acadêmicos",
    description="API RESTful com autenticação JWT, hash seguro de senhas e autorização baseada em perfis.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(evento_router)
app.include_router(participante_router)
app.include_router(inscricao_router)
app.include_router(relatorio_router)


@app.get("/", tags=["Status"])
def status_api():
    return {
        "status": "online",
        "mensagem": "API de Gestão de Eventos Acadêmicos operacional",
        "documentacao": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
