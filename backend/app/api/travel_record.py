from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services import travel_record
from backend.app.schemas.travel_record import RecordFilters, RecordsPage, TravelRecordCreate, TravelRecordRead, TravelRecordUpdate

router = APIRouter(tags=["Records"])

# Temporary user logic
def get_current_user_id() -> int:
    return 1

@router.post("/", response_model=TravelRecordRead)
def create_record(payload: TravelRecordCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return travel_record.create_record(db, user_id, payload)

@router.get("/{record_id}", response_model=TravelRecordRead)
def read_record(record_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rec = travel_record.get_record(db, user_id, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec

@router.patch("/{record_id}", response_model=TravelRecordRead)
def update_record(record_id: int, payload: TravelRecordUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rec = travel_record.update_record(db, user_id, record_id, payload)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec

@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    ok = travel_record.delete_record(db, user_id, record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")
    return

@router.get("/", response_model=RecordsPage)
def list_records(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    q: str | None = Query(default=None),
    country_code: str | None = None,
    region: str | None = None,
    city: str | None = None,
    dest_type: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    order_by: str = "visited_at:desc",
    limit: int = 20,
    offset: int = 0
):
    filters = RecordFilters(
        q=q, country_code=country_code, region=region, city=city, dest_type=dest_type, # type: ignore
        rating_min=rating_min, rating_max=rating_max,
        date_from=date_from, date_to=date_to, # type: ignore
        order_by=order_by, limit=limit, offset=offset
    )
    items, total = travel_record.search_records(db, user_id, filters)
    return {"items": items, "total": total, "limit": limit, "offset": offset}
