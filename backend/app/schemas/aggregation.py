from typing import Annotated
from pydantic import BaseModel, Field
from datetime import date

ISO2 = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]

class AvgRating(BaseModel):
    key: str
    avg_rating: float
    count: int

class TopDestinationPerMonth(BaseModel):
    month: date
    record_id: int
    title: str
    rating: int
    city: str | None
    country_code: ISO2