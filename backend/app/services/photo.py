import os, pathlib, hashlib
from fastapi import UploadFile
import aiofiles

MEDIA_ROOT = "media"
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_MB = 10

async def save_upload(file: UploadFile) -> tuple[str, str, int]:
    raw = await file.read()
    size = len(raw)
    ctype = file.content_type or ""
    if ctype not in ALLOWED:
        raise ValueError("unsupported_mime")
    if size > MAX_MB * 1024 * 1024:
        raise ValueError("file_too_large")

    pathlib.Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
    name = hashlib.sha256(raw).hexdigest()[:20] + ALLOWED[ctype]
    path = os.path.join(MEDIA_ROOT, name)

    async with aiofiles.open(path, "wb") as f:
        await f.write(raw)

    return path, ctype, size
