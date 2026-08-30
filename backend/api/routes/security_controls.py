from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Asset, SecurityControl
from backend.schemas import (
    SecurityControlCreate,
    SecurityControlUpdate,
    SecurityControlResponse,
)

router = APIRouter(prefix="/api/security-controls", tags=["Security Controls"])


@router.post("/", response_model=SecurityControlResponse, status_code=status.HTTP_201_CREATED)
def create_security_control(
    payload: SecurityControlCreate,
    db: Session = Depends(get_db),
):
    if payload.asset_id is not None:
        asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {payload.asset_id} not found.",
            )

    control = SecurityControl(**payload.model_dump())
    db.add(control)
    db.commit()
    db.refresh(control)
    return control


@router.get("/", response_model=List[SecurityControlResponse])
def list_security_controls(db: Session = Depends(get_db)):
    return db.query(SecurityControl).all()


@router.get("/{control_id}", response_model=SecurityControlResponse)
def get_security_control(control_id: int, db: Session = Depends(get_db)):
    control = db.query(SecurityControl).filter(SecurityControl.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security control with id {control_id} not found.",
        )
    return control


@router.put("/{control_id}", response_model=SecurityControlResponse)
def update_security_control(
    control_id: int,
    payload: SecurityControlUpdate,
    db: Session = Depends(get_db),
):
    control = db.query(SecurityControl).filter(SecurityControl.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security control with id {control_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "asset_id" in update_data and update_data["asset_id"] is not None:
        asset_id = update_data["asset_id"]
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found.",
            )

    for field, value in update_data.items():
        setattr(control, field, value)

    db.commit()
    db.refresh(control)
    return control


@router.delete("/{control_id}", status_code=status.HTTP_200_OK)
def delete_security_control(control_id: int, db: Session = Depends(get_db)):
    control = db.query(SecurityControl).filter(SecurityControl.id == control_id).first()
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security control with id {control_id} not found.",
        )

    db.delete(control)
    db.commit()
    return {"message": f"Security control with id {control_id} deleted successfully."}
