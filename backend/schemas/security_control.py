from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SecurityControlBase(BaseModel):
    asset_id: Optional[int] = Field(None, description="Target Asset ID (optional)")
    name: str = Field(..., min_length=1, max_length=255, description="Control name")
    control_type: str = Field(..., description="Type of control (e.g. MFA, EDR, Firewall, etc.)")
    description: Optional[str] = None
    effectiveness: float = Field(0.0, ge=0.0, le=1.0, description="Effectiveness score between 0.0 and 1.0")
    implementation_cost: float = Field(0.0, ge=0.0, description="Implementation cost in INR")
    status: str = Field("Active", description="Status: Active, Inactive, Planned")
    implemented_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Active", "Inactive", "Planned"}
        if v not in allowed:
            raise ValueError(f"status must be one of: {', '.join(sorted(allowed))}")
        return v


class SecurityControlCreate(SecurityControlBase):
    pass


class SecurityControlUpdate(BaseModel):
    asset_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    control_type: Optional[str] = None
    description: Optional[str] = None
    effectiveness: Optional[float] = Field(None, ge=0.0, le=1.0)
    implementation_cost: Optional[float] = Field(None, ge=0.0)
    status: Optional[str] = None
    implemented_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"Active", "Inactive", "Planned"}
            if v not in allowed:
                raise ValueError(f"status must be one of: {', '.join(sorted(allowed))}")
        return v


class SecurityControlResponse(SecurityControlBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
