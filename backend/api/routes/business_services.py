from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import BusinessService
from backend.schemas import (
    BusinessServiceCreate,
    BusinessServiceUpdate,
    BusinessServiceResponse,
)

router = APIRouter(prefix="/api/business-services", tags=["Business Services"])


@router.post("/", response_model=BusinessServiceResponse, status_code=status.HTTP_201_CREATED)
def create_business_service(
    payload: BusinessServiceCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(BusinessService).filter(BusinessService.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Business service with name '{payload.name}' already exists.",
        )

    service = BusinessService(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/", response_model=List[BusinessServiceResponse])
def list_business_services(db: Session = Depends(get_db)):
    return db.query(BusinessService).all()


@router.get("/{service_id}", response_model=BusinessServiceResponse)
def get_business_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BusinessService).filter(BusinessService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business service with id {service_id} not found.",
        )
    return service


@router.put("/{service_id}", response_model=BusinessServiceResponse)
def update_business_service(
    service_id: int,
    payload: BusinessServiceUpdate,
    db: Session = Depends(get_db),
):
    service = db.query(BusinessService).filter(BusinessService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business service with id {service_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != service.name:
        existing = db.query(BusinessService).filter(BusinessService.name == update_data["name"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Business service with name '{update_data['name']}' already exists.",
            )

    for field, value in update_data.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def delete_business_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BusinessService).filter(BusinessService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business service with id {service_id} not found.",
        )

    db.delete(service)
    db.commit()
    return {"message": f"Business service with id {service_id} deleted successfully."}
