from controller.auth_controller import router as auth_router
from controller.evento_controller import router as evento_router
from controller.inscricao_controller import router as inscricao_router
from controller.participante_controller import router as participante_router
from controller.relatorio_controller import router as relatorio_router
from controller.usuario_controller import router as usuario_router

__all__ = [
    "auth_router",
    "evento_router",
    "inscricao_router",
    "participante_router",
    "relatorio_router",
    "usuario_router",
]
