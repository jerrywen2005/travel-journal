from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Tuple
from backend.app.models.travel_record import TravelRecord
from backend.app.schemas.travel_record import RecordFilters, TravelRecordCreate, TravelRecordUpdate

def create_record(db: Session, user_id: int, data: TravelRecordCreate) -> TravelRecord:
    rec = TravelRecord(user_id=user_id, **data.model_dump()) # Auto convert into dict to avoid having to assign every field
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_record(db: Session, user_id: int, record_id: int) -> TravelRecord | None:
    return (
        db.query(TravelRecord)
        .filter(TravelRecord.id == record_id, TravelRecord.user_id == user_id)
        .first()
    )

def update_record(db: Session, user_id: int, record_id: int, data: TravelRecordUpdate) -> TravelRecord | None:
    rec = get_record(db, user_id, record_id)
    if not rec:
        return None
    for k, v in data.model_dump(exclude_unset=True).items(): # Only includes the fields that user sends for update purposes
        setattr(rec, k, v)
    db.commit()
    db.refresh(rec)
    return rec

def delete_record(db: Session, user_id: int, record_id: int) -> bool:
    rec = get_record(db, user_id, record_id)
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True

def search_records(db: Session, user_id: int, filters: RecordFilters) -> Tuple[list[TravelRecord], int]:
    q = db.query(TravelRecord).filter(TravelRecord.user_id == user_id)

    if filters.q:
        like = f"%{filters.q.lower()}%"
        q = q.filter(or_(
            func.lower(TravelRecord.title).like(like),
            func.lower(TravelRecord.notes).like(like),
            func.lower(TravelRecord.city).like(like),
            func.lower(TravelRecord.region).like(like),
        ))

    if filters.country_code:
        q = q.filter(TravelRecord.country_code == filters.country_code)
    if filters.region:
        q = q.filter(TravelRecord.region == filters.region)
    if filters.city:
        q = q.filter(TravelRecord.city == filters.city)
    if filters.dest_type:
        q = q.filter(TravelRecord.destination_type == filters.dest_type)
    if filters.rating_min is not None:
        q = q.filter(TravelRecord.rating >= filters.rating_min)
    if filters.rating_max is not None:
        q = q.filter(TravelRecord.rating <= filters.rating_max)
    if filters.date_from:
        q = q.filter(TravelRecord.visited_at >= filters.date_from)
    if filters.date_to:
        q = q.filter(TravelRecord.visited_at <= filters.date_to)

    # ordering
    field, _, direction = (filters.order_by or "visited_at:desc").partition(":")
    col = getattr(TravelRecord, field, TravelRecord.visited_at)
    if direction.lower() == "asc":
        q = q.order_by(col.asc())
    else:
        q = q.order_by(col.desc())

    total = q.count()
    items = q.offset(filters.offset).limit(filters.limit).all()
    return items, total
