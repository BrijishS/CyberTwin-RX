from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Asset, BusinessService
from backend.schemas import AssetCreate, AssetUpdate, AssetResponse

router = APIRouter(prefix="/api/assets", tags=["Assets"])


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
):
    # Verify business service exists
    bs = db.query(BusinessService).filter(BusinessService.id == payload.business_service_id).first()
    if not bs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business service with id {payload.business_service_id} not found.",
        )

    # Verify duplicate asset name
    existing = db.query(Asset).filter(Asset.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset with name '{payload.name}' already exists.",
        )

    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/", response_model=List[AssetResponse])
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found.",
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "business_service_id" in update_data:
        bs_id = update_data["business_service_id"]
        bs = db.query(BusinessService).filter(BusinessService.id == bs_id).first()
        if not bs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business service with id {bs_id} not found.",
            )

    if "name" in update_data and update_data["name"] != asset.name:
        existing = db.query(Asset).filter(Asset.name == update_data["name"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset with name '{update_data['name']}' already exists.",
            )

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_200_OK)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found.",
        )

    db.delete(asset)
    db.commit()
    return {"message": f"Asset with id {asset_id} deleted successfully."}
