# app/api/routers/users.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.users import user_signup_service, authenticate_user_service, create_user_token, get_user_by_id_service, get_all_users_service, update_user_service, delete_user_service, get_current_active_user
from app.database import get_db
from app.schemas.users import SignUp, UserLogin, UserResponse, SingleUserResponse, LoginSuccessResponse
from app.schemas.common import APIResponse # Import APIResponse

# The router should be defined in this file, not imported from app.api.router.users
# Assuming 'router' is initialized here or in a main `app` file.
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SingleUserResponse)
async def register_new_user(user: SignUp, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    new_user = await user_signup_service(user, db)
    return SingleUserResponse(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
        data=UserResponse(
            user_id=str(new_user.user_id), # Ensure user_id is str
            user_name=new_user.user_name,
            created_at=new_user.created_at
        )
    )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginSuccessResponse)
async def login_user(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return access token"""
    authenticated_user = await authenticate_user_service(user_login, db)

    # Create access token
    access_token = create_user_token(authenticated_user.user_name)

    return LoginSuccessResponse(
        status_code=status.HTTP_200_OK,
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user_details=UserResponse(
            user_id=str(authenticated_user.user_id), # Ensure user_id is str
            user_name=authenticated_user.user_name,
            created_at=authenticated_user.created_at
        )
    )

# CRUD Operations for Users

@router.get("/{user_id}", response_model=SingleUserResponse)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_active_user)):
    """Get a user by ID"""
    user = await get_user_by_id_service(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return SingleUserResponse(
        status_code=status.HTTP_200_OK,
        message="User retrieved successfully",
        data=UserResponse(
            user_id=str(user.user_id),
            user_name=user.user_name,
            created_at=user.created_at
        )
    )

@router.get("/", response_model=APIResponse[list[UserResponse]])
async def get_all_users(db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_active_user)):
    """Get all users"""
    users = await get_all_users_service(db)
    user_responses = [
        UserResponse(user_id=str(user.user_id), user_name=user.user_name, created_at=user.created_at)
        for user in users
    ]
    return APIResponse[list[UserResponse]](
        status_code=status.HTTP_200_OK,
        message="Users retrieved successfully",
        data=user_responses
    )

@router.put("/{user_id}", response_model=SingleUserResponse)
async def update_user(user_id: str, user_update: SignUp, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_active_user)):
    """Update a user"""
    updated_user = await update_user_service(user_id, user_update, db)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return SingleUserResponse(
        status_code=status.HTTP_200_OK,
        message="User updated successfully",
        data=UserResponse(
            user_id=str(updated_user.user_id),
            user_name=updated_user.user_name,
            created_at=updated_user.created_at
        )
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_active_user)):
    """Delete a user"""
    success = await delete_user_service(user_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # For 204 No Content, you typically don't return a body.
    # FastAPI handles this correctly if the function doesn't return anything.
    return