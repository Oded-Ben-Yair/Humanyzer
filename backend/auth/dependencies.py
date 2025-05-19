
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.auth.security import decode_token
from backend.auth.models import TokenData
from backend.repositories.user_db import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.db import get_db
from typing import Optional

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# User repository dependency
async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """
    Dependency to get the user repository.
    
    Args:
        db: Database session
        
    Returns:
        User repository
    """
    return UserRepository(db_session=db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Dependency to get the current authenticated user.
    
    Args:
        token: JWT token from the Authorization header
        user_repository: User repository
        
    Returns:
        The current user if authentication is successful
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode the token
        token_payload = decode_token(token)
        
        # Check if it's an access token
        if token_payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = token_payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await user_repository.get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Dependency to get the current user if authenticated, or None if not.
    
    Args:
        token: JWT token from the Authorization header
        user_repository: User repository
        
    Returns:
        The current user if authenticated, None otherwise
    """
    try:
        return await get_current_user(token, user_repository)
    except HTTPException:
        return None
