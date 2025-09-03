from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.photos import PhotoRead
from backend.app.services.auth import get_current_user
from backend.app.models.travel_record import TravelRecord
from backend.app.services.photo import save_upload
from backend.app.models.user import User

router = APIRouter(prefix="/records", tags=["photos"])

@router.post("/{record_id}/photo", response_model=PhotoRead)
async def upload_record_photo(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rec = (
        db.query(TravelRecord)
        .filter(TravelRecord.id == record_id, TravelRecord.user_id == user.id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")

    try:
        path, ctype, size = await save_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Replace 1:1
    rec.photo_path = path
    rec.photo_content_type = ctype
    rec.photo_size_bytes = size
    db.commit()
    db.refresh(rec)

    # Build PhotoRead
    return {
        "id": rec.id,
        "file_path": rec.photo_path,
        "content_type": rec.photo_content_type,
        "size_bytes": rec.photo_size_bytes,
    }

@router.delete("/{record_id}/photo", status_code=204)
def delete_record_photo(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rec = (
        db.query(TravelRecord)
        .filter(TravelRecord.id == record_id, TravelRecord.user_id == user.id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")

    # clear DB fields, keeps file on disk for simplicity
    rec.photo_path = None
    rec.photo_content_type = None
    rec.photo_size_bytes = None
    db.commit()
