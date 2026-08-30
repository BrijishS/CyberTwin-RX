from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.risk_engine.service import (
    get_all_assets_risk,
    get_asset_risk_by_id,
    get_top_risky_assets,
    get_enterprise_risk_summary,
)

router = APIRouter(prefix="/api/risk", tags=["Risk Quantification"])


@router.get("/summary", response_model=Dict[str, Any])
def read_risk_summary(db: Session = Depends(get_db)):
    return get_enterprise_risk_summary(db)


@router.get("/assets", response_model=List[Dict[str, Any]])
def read_assets_risk(db: Session = Depends(get_db)):
    return get_all_assets_risk(db)


@router.get("/top-assets", response_model=List[Dict[str, Any]])
def read_top_risky_assets(limit: int = 5, db: Session = Depends(get_db)):
    return get_top_risky_assets(db, limit=limit)


@router.get("/assets/{asset_id}", response_model=Dict[str, Any])
def read_asset_risk(asset_id: int, db: Session = Depends(get_db)):
    risk_info = get_asset_risk_by_id(asset_id, db)
    if not risk_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found.",
        )
    return risk_info
