from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.optimizer.service import recommend_security_investments

router = APIRouter(prefix="/api/optimizer", tags=["Investment Optimizer"])


class BudgetRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Available security investment budget in INR (Must be > 0)")


@router.post("/recommend", response_model=Dict[str, Any])
def recommend_investments(payload: BudgetRequest, db: Session = Depends(get_db)):
    if payload.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Budget must be greater than zero.",
        )
    return recommend_security_investments(db, budget=payload.budget)
