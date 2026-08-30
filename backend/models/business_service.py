from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BusinessService(Base):
    __tablename__ = "business_services"

    __table_args__ = (
        CheckConstraint("financial_value >= 0.0", name="check_bs_financial_value_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criticality: Mapped[str] = mapped_column(String(50), nullable=False)
    financial_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="business_service",
        cascade="all, delete-orphan",
    )
