
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base model for user data."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Model for user registration."""
    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Model for user stored in database."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    sso_provider: Optional[str] = None
    sso_provider_id: Optional[str] = None


class UserResponse(UserBase):
    """Model for user response."""
    id: str
    created_at: datetime


class Token(BaseModel):
    """Model for JWT token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Model for JWT token payload."""
    sub: str  # User ID
    exp: Optional[int] = None  # Expiration time
    iat: Optional[int] = None  # Issued at
    type: str  # Token type: "access" or "refresh"
    jti: Optional[str] = None  # JWT ID for token revocation


class TokenData(BaseModel):
    """Model for token data."""
    user_id: str
