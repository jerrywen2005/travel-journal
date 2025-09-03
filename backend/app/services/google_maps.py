from __future__ import annotations
from typing import Any, Dict, List, Optional
import httpx
from backend.env import GOOGLE_MAPS_API_KEY

PLACES_AUTOCOMPLETE = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
PLACES_DETAILS      = "https://maps.googleapis.com/maps/api/place/details/json"

class PlacesError(RuntimeError): ...

def _require_api_key() -> str:
    key = GOOGLE_MAPS_API_KEY
    if not key:
        raise PlacesError("Google Maps API key missing (set GOOGLE_MAPS_API_KEY)")
    return key

async def autocomplete(query: str, session_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns minimal predictions for UI: [{place_id, description}]
    """
    key = _require_api_key()
    params = {
        "input": query,
        "types": "geocode",
        "key": key,
    }
    if session_token:
        params["sessiontoken"] = session_token

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(PLACES_AUTOCOMPLETE, params=params)
        data = r.json()

    if data.get("status") not in {"OK", "ZERO_RESULTS"}:
        raise PlacesError(f"Autocomplete failed: {data.get('status')} - {data.get('error_message')}")

    preds = data.get("predictions", [])
    return [{"place_id": p["place_id"], "description": p.get("description", "")} for p in preds]

def _addr_get(components: list[dict], typ: str, *, short: bool = False) -> Optional[str]:
    for c in components:
        if typ in c.get("types", []):
            return c.get("short_name" if short else "long_name")
    return None

async def place_details(place_id: str) -> Dict[str, Any]:
    """
    Maps Google details to your TravelRecord fields:
    - country_code (ISO2)
    - city
    - latitude, longitude
    - place_external_id
    - title (place name, optional for your 'title' field)
    """
    key = _require_api_key()
    params = {
        "place_id": place_id,
        "key": key,
        "fields": "address_component,geometry,name,place_id",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(PLACES_DETAILS, params=params)
        data = r.json()

    if data.get("status") != "OK":
        raise PlacesError(f"Details failed: {data.get('status')} - {data.get('error_message')}")

    result = data["result"]
    comps = result.get("address_components", [])
    loc   = result.get("geometry", {}).get("location", {})

    country_code = (_addr_get(comps, "country", short=True) or "").upper() or None
    # prefer locality, if not, fallback to admin areas
    city = _addr_get(comps, "locality") or _addr_get(comps, "postal_town") \
        or _addr_get(comps, "administrative_area_level_2") or _addr_get(comps, "administrative_area_level_1")

    lat = loc.get("lat")
    lng = loc.get("lng")

    return {
        "place_external_id": result.get("place_id"),
        "title": result.get("name"), 
        "country_code": country_code,
        "city": city,
        "latitude": lat,
        "longitude": lng,
    }
