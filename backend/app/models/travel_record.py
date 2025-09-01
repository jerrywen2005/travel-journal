from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.base import Base

class TravelRecord(Base):
    __tablename__ = "travel_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    notes = Column(Text)
    country_code = Column(String(2))
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Integer)
    visited_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="records")