from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.models.user import User
from backend.app.services.auth import get_current_user
from backend.app.services.google_maps import autocomplete, place_details, PlacesError

router = APIRouter(tags=["Places"])

@router.get("/autocomplete")
async def places_autocomplete(
    q: str = Query(..., min_length=1, description="Free-text search"),
    session_token: str | None = Query(None, description="Optional Places session token"),
    user: User = Depends(get_current_user),
):
    try:
        return await autocomplete(q, session_token)
    except PlacesError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/details")
async def places_details(
    place_id: str = Query(..., description="Google Place ID"),
    user: User = Depends(get_current_user),
):
    try:
        return await place_details(place_id)
    except PlacesError as e:
        raise HTTPException(status_code=400, detail=str(e))
