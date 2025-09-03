from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from backend.app.schemas.shared import DestinationType

ISO2 = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
Title = Annotated[str, Field(min_length=1, max_length=140)]
City = Annotated[str, Field(max_length=100)]
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]
Rating = Annotated[int, Field(ge=1, le=5)]
PlaceExternalId = Annotated[str, Field(max_length=128)]

class TravelRecordBase(BaseModel):
    title: Title
    notes: str | None = None
    country_code: ISO2
    city: City | None = None
    latitude: Latitude
    longitude: Longitude
    destination_type: DestinationType
    rating: Rating
    visited_at: datetime
    place_external_id: PlaceExternalId | None = None

    @field_validator("country_code")
    @classmethod
    def upper_iso2(cls, v: str) -> str:
        return v.upper()

class TravelRecordCreate(TravelRecordBase):
    pass

class TravelRecordUpdate(BaseModel):
    # Make fields optional here by unioning with None and giving a default
    title: Title | None = None
    notes: str | None = None
    country_code: ISO2 | None = None
    city: City | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    destination_type: DestinationType | None = None
    rating: Rating | None = None
    visited_at: datetime | None = None
    place_external_id: PlaceExternalId | None = None

class PhotoRead(BaseModel):
    id: int
    file_path: str
    content_type: str
    size_bytes: int

class TravelRecordRead(TravelRecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None
    weather_summary: str | None = None
    photo: PhotoRead | None = None
    model_config = ConfigDict(from_attributes=True)

class RecordsPage(BaseModel):
    items: list[TravelRecordRead]
    total: int
    limit: int
    offset: int

class RecordFilters(BaseModel):
    q: Annotated[str, Field(description="Search in title/notes/city/region")] | None = None
    country_code: ISO2 | None = None
    city: City | None = None
    dest_type: DestinationType | None = None
    rating_min: Rating | None = None
    rating_max: Rating | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    near_lat: Latitude | None = None
    near_lon: Longitude | None = None
    near_km: Annotated[float, Field(gt=0)] | None = None
    order_by: Annotated[str, Field(default="visited_at:desc")]
    limit: Annotated[int, Field(default=20, ge=1, le=200)]
    offset: Annotated[int, Field(default=0, ge=0)]
