from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from backend.app.db.base import Base

if TYPE_CHECKING:
    # To get rid of error without having circular imports
    from .travel_record import TravelRecord

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    
    records: Mapped[list["TravelRecord"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    