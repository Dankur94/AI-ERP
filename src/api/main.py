"""
FastAPI application entry point for the Invoice Extraction API.

Run with:
    uvicorn src.api.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.database import init_db
from src.api.routers.alerts import router as alerts_router
from src.api.routers.invoices import router as invoices_router
from src.api.routers.matches import router as matches_router
from src.api.routers.reports import router as reports_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

UPLOAD_DIR: Path = Path(__file__).parent / "storage" / "uploads"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialize DB on startup."""
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Invoice API started. Upload dir: %s", UPLOAD_DIR)
    yield
    logger.info("Invoice API shutting down.")


app = FastAPI(
    title="AI ERP - Invoice Extraction API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Vue dev server at localhost:5173
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

# Include API routers
app.include_router(invoices_router)
app.include_router(matches_router)
app.include_router(reports_router)
app.include_router(alerts_router)

# Mount uploaded PDFs as static files (fallback access)
app.mount(
    "/static/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok", "service": "invoice-extraction-api"}
