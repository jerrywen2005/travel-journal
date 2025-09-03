from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.app.models.travel_record import TravelRecord
from backend.app.schemas.aggregation import AvgRating, TopDestinationPerMonth


def avg_rating_by_country(db: Session, user_id: int) -> list[AvgRating]:
    statement = (
        select(
            TravelRecord.country_code,
            func.avg(TravelRecord.rating),
            func.count(TravelRecord.id),
        )
        .where(TravelRecord.user_id == user_id)
        .group_by(TravelRecord.country_code)
    )
    rows = db.execute(statement).all()
    return [AvgRating(key=c, avg_rating=float(avg), count=int(cnt)) for c, avg, cnt in rows]


def top_destination_per_month(db: Session, user_id: int) -> list[TopDestinationPerMonth]:
    month = func.date_trunc("month", TravelRecord.visited_at).label("month")
    rn = func.row_number().over(
        partition_by=month,
        order_by=(
            TravelRecord.rating.desc(),
            TravelRecord.visited_at.desc(),
            TravelRecord.id.desc(),
        ),
    ).label("rn")

    ranked_subq = (
        select(
            month,
            TravelRecord.id.label("record_id"),
            TravelRecord.title,
            TravelRecord.rating,
            TravelRecord.city,
            TravelRecord.country_code,
            rn,
        )
        .where(TravelRecord.user_id == user_id)
        .subquery()
    )

    statement = (
        select(
            ranked_subq.c.month,
            ranked_subq.c.record_id,
            ranked_subq.c.title,
            ranked_subq.c.rating,
            ranked_subq.c.city,
            ranked_subq.c.country_code,
        )
        .where(ranked_subq.c.rn == 1)
        .order_by(ranked_subq.c.month.asc())
    )

    rows = db.execute(statement).all()
    return [
        TopDestinationPerMonth(
            month=m.date(),
            record_id=rid,
            title=title,
            rating=rating,
            city=city,
            country_code=cc,
        )
        for (m, rid, title, rating, city, cc) in rows
    ]
