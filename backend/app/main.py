from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.generate import router as generate_router


app = FastAPI(title="ContextForge API", version="0.1.0")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generate_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
async def health_alias() -> dict[str, str]:
    return await health()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "ContextForge API",
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
    }
