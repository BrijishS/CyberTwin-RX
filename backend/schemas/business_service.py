from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BusinessServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique business service name")
    description: Optional[str] = None
    criticality: str = Field(..., description="Criticality level: Low, Medium, High, Critical")
    financial_value: float = Field(0.0, ge=0.0, description="Estimated financial value in INR")
    department: Optional[str] = None
    is_active: bool = True

    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: str) -> str:
        allowed = {"Low", "Medium", "High", "Critical"}
        if v not in allowed:
            raise ValueError(f"criticality must be one of: {', '.join(sorted(allowed))}")
        return v


class BusinessServiceCreate(BusinessServiceBase):
    pass


class BusinessServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    criticality: Optional[str] = None
    financial_value: Optional[float] = Field(None, ge=0.0)
    department: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"Low", "Medium", "High", "Critical"}
            if v not in allowed:
                raise ValueError(f"criticality must be one of: {', '.join(sorted(allowed))}")
        return v


class BusinessServiceResponse(BusinessServiceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
