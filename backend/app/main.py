"""
FastAPI application entry point.

Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    This is the modern replacement for @app.on_event("startup").
    Everything before `yield` runs on startup, after `yield` on shutdown.
    """
    # Startup
    print("Initializing database...")
    init_db()
    print("Database initialized.")

    yield  # App runs here

    # Shutdown (cleanup if needed)
    print("Shutting down...")


app = FastAPI(
    title="SpendLens API",
    description="AI-powered spending analyzer",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


# Routers will be included here as we build them
# from app.routers import upload, analysis
# app.include_router(upload.router)
# app.include_router(analysis.router)
