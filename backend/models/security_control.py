from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SecurityControl(Base):
    __tablename__ = "security_controls"

    __table_args__ = (
        CheckConstraint("effectiveness >= 0.0 AND effectiveness <= 1.0", name="check_effectiveness_range"),
        CheckConstraint("implementation_cost >= 0.0", name="check_implementation_cost_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("assets.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    control_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effectiveness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    implementation_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")
    implemented_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="security_controls")
