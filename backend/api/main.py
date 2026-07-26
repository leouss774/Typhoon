"""
FastAPI Application Entrypoint
===============================
Replaces the Hono-based `backend/api/main.ts`.

Mounts CORS, error handlers, and all route modules under their prefixes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.routes.health import router as health_router
from api.routes.auth import router as auth_router
from api.routes.clients import router as client_router
from api.routes.properties import router as property_router
from api.routes.assessments import router as assessment_router
from api.routes.risk import router as risk_router
from api.routes.admin import router as admin_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup/shutdown events."""
    logging.basicConfig(level=logging.INFO)
    logging.info(
        "🚀 Prévia API starting on http://0.0.0.0:%d (env=%s)",
        settings.PORT,
        settings.ENVIRONMENT,
    )
    yield
    logging.info("🛑 Prévia API shutting down")


app = FastAPI(
    title="Prévia Risk Platform API",
    version="0.2.0",
    description="FastAPI backend for insurance risk assessment platform",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
    max_age=86400,
)

# ─── Routes ───────────────────────────────────────────────────────
app.include_router(health_router)           # GET /health
app.include_router(auth_router)             # /api/auth/*
app.include_router(client_router)           # /api/clients/*
app.include_router(property_router)         # /api/properties/*
app.include_router(assessment_router)       # /api/assessments/*
app.include_router(risk_router)             # /api/risk/*
app.include_router(admin_router)            # /api/admin/*

