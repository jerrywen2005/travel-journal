import os
from dotenv import load_dotenv

def get_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"{key} is not set in your environment!")
    return value

load_dotenv()

DATABASE_URL = get_env("DATABASE_URL")
JWT_SECRET = get_env("JWT_SECRET")
GOOGLE_MAPS_API_KEY = get_env("GOOGLE_MAPS_API_KEY")