from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, DateTime, ForeignKey, CheckConstraint, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from backend.app.models.user import User
from backend.app.schemas.shared import DestinationType

class TravelRecord(Base):
    __tablename__ = "travel_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(140), nullable=False)
    notes: Mapped[str | None] = mapped_column(String)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100))

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    destination_type: Mapped[DestinationType] = mapped_column(
        SAEnum(DestinationType, name="destination_type"),
        nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    visited_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    place_external_id: Mapped[str | None] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_travel_records_rating_1_5"),
    )

    user: Mapped["User"] = relationship(back_populates="records")
