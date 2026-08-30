from backend.api.routes.business_services import router as business_services_router
from backend.api.routes.assets import router as assets_router
from backend.api.routes.vulnerabilities import router as vulnerabilities_router
from backend.api.routes.security_controls import router as security_controls_router
from backend.api.routes.risk import router as risk_router
from backend.api.routes.digital_twin import router as digital_twin_router
from backend.api.routes.optimizer import router as optimizer_router
from backend.api.routes.simulation import router as simulation_router
from backend.api.routes.ai import router as ai_router

__all__ = [
    "business_services_router",
    "assets_router",
    "vulnerabilities_router",
    "security_controls_router",
    "risk_router",
    "digital_twin_router",
    "optimizer_router",
    "simulation_router",
    "ai_router",
]
