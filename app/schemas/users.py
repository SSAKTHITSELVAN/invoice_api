# app/schemas/users.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Import the common APIResponse
from app.schemas.common import APIResponse

class SignUp(BaseModel):
    user_name: str
    password: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    user_name: str
    password: str

class UserResponse(BaseModel):
    user_id: str  # Changed to str to match uuid.uuid4()
    user_name: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# New response models using the common APIResponse template
class SingleUserResponse(APIResponse[UserResponse]):
    """Response model for a single user."""
    pass

class LoginSuccessResponse(APIResponse): # LoginResponse might not always contain data in the 'data' field directly, so just base APIResponse
    """Response model for successful login."""
    access_token: str
    token_type: str
    user_details: UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str

# Keep LoginResponse for now, but the API endpoint will return LoginSuccessResponse
# class LoginResponse(BaseModel):
#     access_token: str
#     token_type: str
#     user_details: UserResponse