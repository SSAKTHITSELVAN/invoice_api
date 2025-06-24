# app/api/routers/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.users import user_signup_service, authenticate_user_service, create_user_token
from app.database import get_db
from app.schemas.users import SignUp, UserLogin, UserResponse, LoginResponse
from app.api.router.users import router


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_new_user(user: SignUp, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    new_user = await user_signup_service(user, db)
    return UserResponse(
        user_id=new_user.user_id,
        user_name=new_user.user_name,
        created_at=new_user.created_at
    )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login_user(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return access token"""
    authenticated_user = await authenticate_user_service(user_login, db)
    
    # Create access token
    access_token = create_user_token(authenticated_user.user_name)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_details=UserResponse(
            user_id=authenticated_user.user_id,
            user_name=authenticated_user.user_name,
            created_at=authenticated_user.created_at
        )
    )