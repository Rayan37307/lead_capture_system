from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.schemas.auth import Token, UserCreateRequest, UserResponse
from app.models.user import UserCreate, UserInDB, User
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config.settings import settings
from app.database.mongodb import get_database
from pymongo.errors import DuplicateKeyError


router = APIRouter()

# Dependency to get the User collection
async def get_user_collection():
    db = await get_database()
    return db.users


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateRequest,
    users_collection = Depends(get_user_collection)
):
    # Check if user already exists
    if await users_collection.find_one({"email": user_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user in DB
    user_in_db = UserCreate(
        email=user_data.email,
        tenant_id=user_data.tenant_id,
        password=hashed_password
    )

    try:
        result = await users_collection.insert_one(user_in_db.model_dump(by_alias=True, exclude=["password"]))
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        return User(**created_user)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered (duplicate key)"
        )


@router.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    users_collection = Depends(get_user_collection)
):
    user_dict = await users_collection.find_one({"email": username})
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    user_in_db = UserInDB(**user_dict) # This now includes tenant_id

    if not verify_password(password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user_in_db.email,
            "tenant_id": str(user_in_db.tenant_id) # Ensure tenant_id is string for JWT
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
