# Authentication Service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import Users
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings

async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Authenticate user and return user object if valid"""
    query_result = await db.execute(select(Users).where(Users.user_name == username))
    user = query_result.scalar_one_or_none()
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_user_by_username(db: AsyncSession, username: str):
    """Get user by username"""
    query_result = await db.execute(select(Users).where(Users.user_name == username))
    return query_result.scalar_one_or_none()

def create_user_token(username: str):
    """Create access token for user"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return access_token

# 5. dependencies.py - JWT Dependency
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.services.auth_service import get_user_by_username
from app.database import get_db

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise credentials_exception
    
    user = await get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

