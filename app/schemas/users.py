# app/schemas/users.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SignUp(BaseModel):
    user_name: str
    password: str
    
    class Config:
        orm_mode = True
        from_attributes = True  # Updated for Pydantic v2

class UserLogin(BaseModel):
    user_name: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_details: UserResponse