from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.seed import seed_data
from backend.api import (
    business_services_router,
    assets_router,
    vulnerabilities_router,
    security_controls_router,
    risk_router,
    digital_twin_router,
    optimizer_router,
    simulation_router,
    ai_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed data if missing on startup
    init_db()
    try:
        seed_data()
    except Exception as e:
        print(f"Database seed check note: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Cyber Risk Digital Twin & Security Investment Optimizer",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local & cloud Streamlit dashboard deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(business_services_router)
app.include_router(assets_router)
app.include_router(vulnerabilities_router)
app.include_router(security_controls_router)
app.include_router(risk_router)
app.include_router(digital_twin_router)
app.include_router(optimizer_router)
app.include_router(simulation_router)
app.include_router(ai_router)


@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "phase": settings.PHASE,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
