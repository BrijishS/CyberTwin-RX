from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique asset name")
    asset_type: str = Field(..., description="Type of asset (e.g. Server, Database, API, etc.)")
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    business_service_id: int = Field(..., description="Associated Business Service ID")
    criticality: str = Field(..., description="Criticality level: Low, Medium, High, Critical")
    financial_value: float = Field(0.0, ge=0.0, description="Estimated financial value in INR")
    internet_exposed: bool = False
    environment: Optional[str] = Field(None, description="Environment: Production, Development, Testing, Staging")
    owner_department: Optional[str] = None
    is_active: bool = True

    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: str) -> str:
        allowed = {"Low", "Medium", "High", "Critical"}
        if v not in allowed:
            raise ValueError(f"criticality must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"Production", "Development", "Testing", "Staging"}
            if v not in allowed:
                raise ValueError(f"environment must be one of: {', '.join(sorted(allowed))}")
        return v


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    asset_type: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    business_service_id: Optional[int] = None
    criticality: Optional[str] = None
    financial_value: Optional[float] = Field(None, ge=0.0)
    internet_exposed: Optional[bool] = None
    environment: Optional[str] = None
    owner_department: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"Low", "Medium", "High", "Critical"}
            if v not in allowed:
                raise ValueError(f"criticality must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"Production", "Development", "Testing", "Staging"}
            if v not in allowed:
                raise ValueError(f"environment must be one of: {', '.join(sorted(allowed))}")
        return v


class AssetResponse(AssetBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
