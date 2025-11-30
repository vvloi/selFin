"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routers import (
    auth_router,
    transactions_router,
    budgets_router,
    recurring_router,
    analytics_router
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    root_path=settings.root_path
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(auth_router.wallet_router, prefix="/api/v1")
app.include_router(transactions_router.category_router, prefix="/api/v1")
app.include_router(transactions_router.router, prefix="/api/v1")
app.include_router(budgets_router.router, prefix="/api/v1")
app.include_router(recurring_router.router, prefix="/api/v1")
app.include_router(analytics_router.router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
