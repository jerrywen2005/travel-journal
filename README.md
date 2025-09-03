# 🌍 Travel Journal API

A REST API built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, and **Angular** to record travel experiences, filter/query them, and compute aggregations. Built for a take home project for App Team Carolina’s F25 Backend Developer interview.

---

## 🚀 Features

- **Users**: signup/login (basic auth)
- **Travel Records**:
  - Create, Read (with filtering/search), Update, Delete
  - Validation for ISO country codes, coordinates, rating, etc.
- **Aggregations**:
  - Average rating by country
  - Top destination per month
- **Photos**:
  - Current: one photo per record (1:1, simple)
  - Planned: multiple photos per record (1:N, via `photos` table)
- **Docs**: Interactive OpenAPI at `/docs`
- **Integrations**: Google Places Autocomplete/Details (server-side), frontend map via Leaflet (no browser key)
- **Frontend**: Angular (standalone components, reactive forms), HTTP interceptor for JWT
- **Dev orchestration**: Procfile + Honcho, Postgres via Docker, Caddy as reverse proxy

---

## 🛠️ Tech Stack

- **FastAPI** (Python 3.11)
- **SQLAlchemy 2.0** (modern style with `Mapped[]` + `mapped_column`)
- **PostgreSQL** (via Docker)
- **Alembic** for database migrations
- **Pydantic v2** for validation
- **Honcho** to run processes from `Procfile`
- **Caddy** reverse proxy
- **Angular 18** for basic frontend

---

## ⚡ Quick Start

```bash
# 1. clone & install
git clone https://github.com/yourname/travel-journal-api.git
cd travel-journal-api
pip install -r requirements.txt

# 2. start db (docker compose)
docker compose up -d db

# 3. migrate
alembic upgrade head

# 4. run services (api + frontend + caddy) via honcho
honcho start

# default ports
# Caddy:     http://localhost:1660
# API:       http://localhost:1661
# Frontend:  http://localhost:1662

API Reference 
All routes require Authorization: Bearer <token> except for Auth routes.

Auth
- POST /api/auth/signup → {id, name, email}
- POST /api/auth/login → {access_token, token_type}
- POST /api/auth/token (OAuth2 form for OpenAPI’s “Authorize”)

Records
- POST /api/travel_record/records → TravelRecordRead
- GET /api/travel_record/records/{id} → TravelRecordRead
- PATCH /api/travel_record/records/{id} → TravelRecordRead
- DELETE /api/travel_record/records/{id} → 204
- GET /api/travel_record/records → RecordsPage
    Query (RecordFilters):
    q, country_code, city, dest_type, rating_min, rating_max, date_from, date_to, order_by=visited_at:desc, limit=20, offset=0
    q searches in title/notes/city (case-insensitive)
    order_by supports fields like visited_at, rating, title with :asc|:desc

Photos (1:1)
- POST /api/travel_record/records/{id}/photo → PhotoRead
- DELETE /api/travel_record/records/{id}/photo → 204
- Allowed types: image/jpeg, image/png, image/webp, image/gif. Files go to MEDIA_ROOT (default ./media). FastAPI mounts /media so images render in the table.

Aggregations
- GET /api/aggregations/avg-rating-by-country → [{ key, avg_rating, count }]
- GET /api/aggregations/top-destination-per-month → [{ month, record_id, title, rating, city, country_code }]

Google_Maps:
- GET /api/places/autocomplete?q=TEXT → [{place_id, description}]
- GET /api/places/details?place_id=... → { place_external_id, title, country_code, city, latitude, longitude }



Challenges & Fixes

Ports / Honcho / Caddy mismatch
- Problem: Honcho failed to launch DB because ports were inconsistent
- I fixed by standardizing: Caddy: 1660 → proxies API/docs (1661) and frontend (1662). DB: Postgres on default 5432.

SQLAlchemy 2.0 Migration
- Moved from legacy .query patterns to 2.0 (select(...), mapped_column, relationship).
- Better type checking and fewer runtime surprises.

Schema ↔ Model mismatches
- Fixed by adding Pydantic v2 validators (ISO2, lat/lon, rating) and keeping column names aligned with schemas.


Circular imports
- Solved by using if TYPE_CHECKING to avoid runtime cycles (User.records, TravelRecord.user).

User vs user_id
- get_current_user returned User object; services expected int
- Fixed services to receive user.id rather than a full User ORM object where appropriate.

Leaflet SSR issues
- Replacing Google Maps for map display to avoid exposing Google Maps API key



Future Improvements (if given more time)
- Multi-photo support (1:N photos table, cover photo, gallery view)
- 3rd-party enrichments with weather summary
- Testing
- Better docs
- Improved frontend


Error Examples:


- 401 Unauthorized
    Happens when the Authorization header is missing or token is invalid.

    GET /api/travel_record/records
    

    {
    "detail": "Could not validate credentials"
    }

- 404 Not Found
    Happens when a record doesn’t exist or doesn’t belong to the current user.

    GET /api/travel_record/records/999

    {
    "detail": "Record not found"
    }

- 422 Validation Error


    {
        "detail": [
            {
            "type": "greater_than_equal",
            "loc": ["body", "rating"],
            "msg": "Input should be greater than or equal to 1",
            "input": 0,
            "ctx": {"ge": 1}
            }
        ]
    }

    Another example: invalid country_code not matching ISO2 convention.

    {
        "detail": [
            {
            "type": "string_pattern_mismatch",
            "loc": ["body", "country_code"],
            "msg": "String should match pattern '^[A-Z]{2}$'",
            "input": "usa",
            "ctx": {"pattern": "^[A-Z]{2}$"}
            }
        ]
    }


- 400 Bad Request
    Happens if you try to register with an existing email.

    POST /api/auth/signup

    {
    "detail": "Email already registered"
    }`


Architecture & Folder Layout:

.devcontainer/
    devcontainer.json
    docker-compose.yml
    dockerfile
backend/
  app/
    api/
      routes/
        auth.py              # signup/login/token
        travel_record.py           # CRUD + filtering
        aggregations.py      # avg-by-country, top-destination-per-month
        places.py            # Google Places autocomplete/details, (optional) create-from-place
        photos.py            # 1:1 upload + delete
    core/
      config.py              # settings (GOOGLE_MAPS_API_KEY, MEDIA_ROOT, etc.)
    db/
      base.py                # SQLAlchemy Base
      session.py             # SessionLocal + get_db dep
    models/
      user.py
      travel_record.py
    schemas/
      user.py
      shared.py              # DestinationType enum (StrEnum)
      travel_record.py       # Pydantic models for records + filters + read/create/update
      aggregation.py         # AvgRating, TopDestinationPerMonth
    services/
      auth.py                # JWT, password hashing, get_current_user
      travel_record.py       # CRUD + search
      aggregation.py         # SQLA queries for aggregations
      google_maps.py       # httpx calls to Google (autocomplete, details)
      photo.py               # store/replace/delete image files
    main.py                  # FastAPI app, router mounting, static media, startup
  env.py / .env              # secrets (JWT, GOOGLE_MAPS_API_KEY)
frontend/
  src/
    app/
      records/
        entries.page.ts/html/css   # form + search + map + table + photo upload
        records.service.ts         # CRUD + photo HTTP calls
      places/
        places.service.ts          # calls backend /places/*
        map.component.ts           # Leaflet map (SSR-safe)
      auth/
        auth.interceptor.ts          # attaches Authorization header
    styles.css                     # imports Leaflet CSS
migrations/                         # Alembic
Caddyfile                          # reverse proxy
Procfile / honcho                  # run services on fixed ports
