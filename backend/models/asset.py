from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Asset(Base):
    __tablename__ = "assets"

    __table_args__ = (
        CheckConstraint("financial_value >= 0.0", name="check_asset_financial_value_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    business_service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("business_services.id"), nullable=False
    )
    criticality: Mapped[str] = mapped_column(String(50), nullable=False)
    financial_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    internet_exposed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    environment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    owner_department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    business_service: Mapped["BusinessService"] = relationship(
        "BusinessService", back_populates="assets"
    )
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship(
        "Vulnerability",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
    security_controls: Mapped[List["SecurityControl"]] = relationship(
        "SecurityControl",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
