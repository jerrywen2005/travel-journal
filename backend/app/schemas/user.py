from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True