# app/services/users.py
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.users import Users
from app.schemas.users import SignUp, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token
from datetime import timedelta
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db

async def user_signup_service(user: SignUp, db: AsyncSession) -> Users:
    """Service function for user signup"""

    # Check if user already exists
    query = select(Users).where(Users.user_name == user.user_name)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = Users(
        user_name=user.user_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user_service(user_login: UserLogin, db: AsyncSession) -> Users:
    """Service function for user authentication"""

    # Find user by username
    query = select(Users).where(Users.user_name == user_login.user_name)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return user

def create_user_token(username: str) -> str:
    """Create access token for user"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    return access_token

# OAuth2 scheme - points to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login") # Updated tokenUrl to match your router prefix

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Users:
    """
    Dependency to get current authenticated user from JWT token
    """
    # Verify the token and get username
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    query = select(Users).where(Users.user_name == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_active_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Dependency to get current active user (extend this if you have user status)
    """
    # You can add additional checks here like user.is_active if you have that field
    return current_user

# New CRUD Service Functions

async def get_user_by_id_service(user_id: str, db: AsyncSession) -> Users | None:
    """Service function to get a user by their ID."""
    query = select(Users).where(Users.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_all_users_service(db: AsyncSession) -> list[Users]:
    """Service function to get all users."""
    query = select(Users)
    result = await db.execute(query)
    return result.scalars().all()

async def update_user_service(user_id: str, user_update: SignUp, db: AsyncSession) -> Users | None:
    """Service function to update a user."""
    # First, check if the user exists
    user = await get_user_by_id_service(user_id, db)
    if not user:
        return None

    # Update fields
    user.user_name = user_update.user_name
    user.hashed_password = get_password_hash(user_update.password) # Re-hash password on update

    await db.commit()
    await db.refresh(user)
    return user

async def delete_user_service(user_id: str, db: AsyncSession) -> bool:
    """Service function to delete a user."""
    query = delete(Users).where(Users.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0 # Returns True if a row was deleted, False otherwise