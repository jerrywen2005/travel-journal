from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.services.auth import get_current_user
from backend.app.db.session import get_db
from backend.app.schemas.aggregation import AvgRating, TopDestinationPerMonth
from backend.app.services.aggregation import avg_rating_by_country, top_destination_per_month

router = APIRouter(tags=["aggregations"])

@router.get("/avg-rating-by-country", response_model=list[AvgRating])
def get_avg_by_country(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    return avg_rating_by_country(db, user_id)

@router.get("/top-destination-per-month", response_model=list[TopDestinationPerMonth])
def get_top_per_month(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    return top_destination_per_month(db, user_id)