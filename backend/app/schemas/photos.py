from pydantic import BaseModel

class PhotoRead(BaseModel):
    id: int
    file_path: str
    content_type: str
    size_bytes: int