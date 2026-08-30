from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.simulation.service import run_asset_simulation, run_portfolio_simulation

router = APIRouter(prefix="/api/simulation", tags=["What-If Simulator"])


class WhatIfRequest(BaseModel):
    asset_id: int = Field(..., description="ID of the asset to simulate")
    control_type: str = Field(..., description="Security control type or scenario e.g. MFA, EDR, Patch vulnerability")
    effectiveness: float = Field(0.80, ge=0.0, le=1.0, description="Control effectiveness (0.0 to 1.0)")
    patch_cve_id: Optional[str] = Field(None, description="Optional CVE ID to patch")


class PortfolioWhatIfRequest(BaseModel):
    controls: List[Dict[str, Any]] = Field(default=[], description="List of controls selected from optimizer or custom list")


@router.post("/what-if", response_model=Dict[str, Any])
def simulate_what_if(payload: WhatIfRequest, db: Session = Depends(get_db)):
    try:
        return run_asset_simulation(
            asset_id=payload.asset_id,
            control_type=payload.control_type,
            effectiveness=payload.effectiveness,
            patch_cve_id=payload.patch_cve_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/portfolio", response_model=Dict[str, Any])
def simulate_portfolio(payload: PortfolioWhatIfRequest, db: Session = Depends(get_db)):
    return run_portfolio_simulation(
        simulated_controls=payload.controls,
        db=db,
    )
