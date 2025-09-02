from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.travel_record import TravelRecord

def avg_rating_by_country(db: Session, user_id: int) -> list[dict[str, Any]]:
    rows = (
        db.query(TravelRecord.country_code,
                 func.avg(TravelRecord.rating),
                 func.count(TravelRecord.id))
        .filter(TravelRecord.user_id == user_id)
        .group_by(TravelRecord.country_code)
        .all()
    )
    return [
        {"country_code": c, "avg_rating": float(avg), "count": int(cnt)}
        for c, avg, cnt in rows
    ]

def top_rated_per_city(db: Session, user_id: int) -> list[dict[str, Any]]:
    # gives max rating for each city
    subq = (
        db.query(TravelRecord.city,
                 func.max(TravelRecord.rating).label("max_rating"))
        .filter(TravelRecord.user_id == user_id)
        .group_by(TravelRecord.city)
        .subquery()
    )
    rows = (
        db.query(TravelRecord)
        .join(subq, (TravelRecord.city == subq.c.city) &
                    (TravelRecord.rating == subq.c.max_rating))
        .filter(TravelRecord.user_id == user_id)
        .all()
    )
    return [
        {
            "city": r.city,
            "title": r.title,
            "rating": r.rating,
            "country_code": r.country_code,
            "id": r.id,
        }
        for r in rows
    ]
