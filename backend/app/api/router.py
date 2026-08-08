from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import leads, outreach, search

api_router = APIRouter(prefix="/api")
api_router.include_router(search.router)
api_router.include_router(leads.router)
api_router.include_router(outreach.router)
