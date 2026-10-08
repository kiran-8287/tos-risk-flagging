from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, analysis
from app.core.config import settings
from app.ml.model_loader import model_loader


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Terms of Service risk analysis API.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{settings.FRONTEND_PORT}",
        f"http://127.0.0.1:{settings.FRONTEND_PORT}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["analysis"])


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.on_event("startup")
def startup_event():
    try:
        model_loader.load()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Failed to load model on startup: %s", exc)
