from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.schemas.auth import Token, UserCreateRequest, UserResponse
from app.models.user import User, UserInDB
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config.settings import settings
from app.database import sqlite_handler

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreateRequest):
    """
    Register a new user for a specific tenant.
    """
    # Check if user already exists for this tenant
    existing_user = await sqlite_handler.get_user_by_email(user_data.tenant_id, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered for this tenant"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user in DB
    try:
        created_user_dict = await sqlite_handler.create_user(
            tenant_id=user_data.tenant_id,
            email=user_data.email,
            hashed_password=hashed_password
        )
        return User.model_validate(created_user_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {e}"
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    tenant_id: str = Form(...) # Added for multi-tenancy
):
    """
    Authenticate user and return a JWT access token.
    """
    user_dict = await sqlite_handler.get_user_by_email(tenant_id, username)
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email, password, or tenant ID")

    user_in_db = UserInDB.model_validate(user_dict)

    if not verify_password(password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email, password, or tenant ID")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user_in_db.email,
            "tenant_id": user_in_db.tenant_id
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
