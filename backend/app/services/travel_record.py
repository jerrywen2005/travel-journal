from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select
from backend.app.models.travel_record import TravelRecord
from backend.app.schemas.travel_record import RecordFilters, TravelRecordCreate, TravelRecordUpdate

def create_record(db: Session, user_id: int, data: TravelRecordCreate) -> TravelRecord:
    rec = TravelRecord(user_id=user_id, **data.model_dump()) # Auto convert into dict to avoid having to assign every field
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_record(db: Session, user_id: int, record_id: int) -> TravelRecord | None:
    statement = (
        select(TravelRecord)
        .where(TravelRecord.id == record_id, TravelRecord.user_id == user_id)
        .limit(1)
    )
    return db.execute(statement).scalars().first()

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

def search_records(db: Session, user_id: int, filters: RecordFilters) -> tuple[list[TravelRecord], int]:
    statement = select(TravelRecord).where(TravelRecord.user_id == user_id)

    if filters.q:
        like = f"%{filters.q.lower()}%"
        q = statement.filter(or_(
            func.lower(TravelRecord.title).like(like),
            func.lower(TravelRecord.notes).like(like),
            func.lower(TravelRecord.city).like(like),
        ))

    # Exact search
    if filters.country_code:
        q = statement.filter(TravelRecord.country_code == filters.country_code)
    if filters.city:
        q = statement.filter(TravelRecord.city == filters.city)
    if filters.dest_type:
        q = statement.filter(TravelRecord.destination_type == filters.dest_type)
    
    # Numeric and date range filter
    if filters.rating_min is not None:
        q = statement.filter(TravelRecord.rating >= filters.rating_min)
    if filters.rating_max is not None:
        q = statement.filter(TravelRecord.rating <= filters.rating_max)
    if filters.date_from:
        q = statement.filter(TravelRecord.visited_at >= filters.date_from)
    if filters.date_to:
        q = statement.filter(TravelRecord.visited_at <= filters.date_to)

    # ordering
    field, _, direction = (filters.order_by or "visited_at:desc").partition(":")
    col = getattr(TravelRecord, field, TravelRecord.visited_at)
    statement = statement.order_by(col.asc() if direction.lower() == "asc" else col.desc())
    
    count_query = select(func.count()).select_from(statement.order_by(None).subquery())
    row_count = db.execute(count_query).scalar_one()

    results_query = statement.offset(filters.offset).limit(filters.limit)
    result_items = db.execute(results_query).scalars().all()

    return result_items, int(row_count) # type: ignore