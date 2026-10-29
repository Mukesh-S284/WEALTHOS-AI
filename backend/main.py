"""Main FastAPI application entrypoint for WealthOS AI."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.exceptions import WealthOSException

# Routers
from backend.api.v1.auth import router as auth_router
from backend.api.v1.users import router as users_router
from backend.api.v1.transactions import router as transactions_router
from backend.api.v1.budgets import router as budgets_router
from backend.api.v1.savings import router as savings_router
from backend.api.v1.debts import router as debts_router
from backend.api.v1.purchases import router as purchases_router
from backend.api.v1.scenarios import router as scenarios_router
from backend.api.v1.market import router as market_router
from backend.api.v1.portfolio import router as portfolio_router
from backend.api.v1.simulation import router as simulation_router
from backend.api.v1.assistant import router as assistant_router
from backend.api.v1.knowledge import router as knowledge_router
from backend.api.v1.learning import router as learning_router
from backend.api.v1.scam import router as scam_router
from backend.api.v1.reports import router as reports_router
from backend.api.v1.decision import router as decision_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Explainable AI-Powered Personal Finance, Investment Intelligence and Wealth Planning Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(WealthOSException)
async def wealthos_exception_handler(request: Request, exc: WealthOSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.detail
        },
        headers=exc.headers
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    # Do not leak internal exception details to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request."
        }
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include Module Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(budgets_router, prefix="/api/v1")
app.include_router(savings_router, prefix="/api/v1")
app.include_router(debts_router, prefix="/api/v1")
app.include_router(purchases_router, prefix="/api/v1")
app.include_router(scenarios_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(assistant_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(learning_router, prefix="/api/v1")
app.include_router(scam_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(decision_router, prefix="/api/v1")
