from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.models.user import User
from app.database import sqlite_handler
from app.config.settings import settings


# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.API_V1_STR + "/auth/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash for the given password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default 15 minutes

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")  # Extract tenant_id from token
        if email is None or tenant_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_dict = await sqlite_handler.get_user_by_email(tenant_id=tenant_id, email=email)
    if user_dict is None:
        raise credentials_exception
    return User.model_validate(user_dict)


# These constants were previously defined in the main module
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM