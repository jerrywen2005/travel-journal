from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.api import auth, travel_record

app = FastAPI()

# Serve Angular static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.include_router(auth.router, prefix="/api/auth")
app.include_router(travel_record.router, prefix="/api/travel_record")