from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Asset, Vulnerability
from backend.schemas import (
    VulnerabilityCreate,
    VulnerabilityUpdate,
    VulnerabilityResponse,
)

router = APIRouter(prefix="/api/vulnerabilities", tags=["Vulnerabilities"])


@router.post("/", response_model=VulnerabilityResponse, status_code=status.HTTP_201_CREATED)
def create_vulnerability(
    payload: VulnerabilityCreate,
    db: Session = Depends(get_db),
):
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {payload.asset_id} not found.",
        )

    vulnerability = Vulnerability(**payload.model_dump())
    db.add(vulnerability)
    db.commit()
    db.refresh(vulnerability)
    return vulnerability


@router.get("/", response_model=List[VulnerabilityResponse])
def list_vulnerabilities(db: Session = Depends(get_db)):
    return db.query(Vulnerability).all()


@router.get("/{vulnerability_id}", response_model=VulnerabilityResponse)
def get_vulnerability(vulnerability_id: int, db: Session = Depends(get_db)):
    vulnerability = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vulnerability with id {vulnerability_id} not found.",
        )
    return vulnerability


@router.put("/{vulnerability_id}", response_model=VulnerabilityResponse)
def update_vulnerability(
    vulnerability_id: int,
    payload: VulnerabilityUpdate,
    db: Session = Depends(get_db),
):
    vulnerability = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vulnerability with id {vulnerability_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "asset_id" in update_data:
        asset_id = update_data["asset_id"]
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found.",
            )

    for field, value in update_data.items():
        setattr(vulnerability, field, value)

    db.commit()
    db.refresh(vulnerability)
    return vulnerability


@router.delete("/{vulnerability_id}", status_code=status.HTTP_200_OK)
def delete_vulnerability(vulnerability_id: int, db: Session = Depends(get_db)):
    vulnerability = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if not vulnerability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vulnerability with id {vulnerability_id} not found.",
        )

    db.delete(vulnerability)
    db.commit()
    return {"message": f"Vulnerability with id {vulnerability_id} deleted successfully."}
