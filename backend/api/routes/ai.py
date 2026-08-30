from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.ai.service import get_ai_status, predict_vulnerability_exploitation, get_top_ml_threats

router = APIRouter(prefix="/api/ai", tags=["AI & Machine Learning"])


@router.get("/status", response_model=Dict[str, Any])
def read_ai_status():
    """
    Get current Machine Learning model loaded status, training metrics, and metadata.
    """
    return get_ai_status()


@router.get("/vulnerabilities/{vulnerability_id}", response_model=Dict[str, Any])
def predict_vulnerability(
    vulnerability_id: int,
    db: Session = Depends(get_db)
):
    """
    Get ML exploitation probability and risk level prediction for a specific vulnerability.
    """
    res = predict_vulnerability_exploitation(vulnerability_id, db)
    if not res:
        raise HTTPException(
            status_code=404,
            detail=f"Vulnerability with ID {vulnerability_id} not found."
        )
    return res


@router.get("/top-threats", response_model=List[Dict[str, Any]])
def read_top_ml_threats(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top N vulnerabilities prioritized by ML exploitation probability.
    """
    return get_top_ml_threats(db, limit=limit)
