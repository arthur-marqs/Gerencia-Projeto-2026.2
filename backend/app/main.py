
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.families import router as families_router
from app.api.routes.health import router as health_router
from app.api.routes.produtos import router as produtos_router


app = FastAPI(
    title="SetupFlow API",
    description="API do sistema de planejamento da produção.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Autenticação"],
)
app.include_router(
    produtos_router,
    prefix="/api/produtos",
    tags=["Produtos"],
)
app.include_router(families_router, prefix="/api")
