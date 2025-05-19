
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth.models import UserCreate, UserResponse, Token, UserLogin
from backend.auth.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    revoke_token,
    revoke_all_user_tokens
)
from backend.repositories.user_db import UserRepository
from backend.auth.dependencies import get_current_user, get_user_repository, oauth2_scheme
from backend.auth.redis_rate_limiter import limit_login_attempts
from datetime import datetime
import uuid
from backend.config import settings

# Import SSO controller
from backend.auth.sso.ssoController import router as sso_router

router = APIRouter(prefix="/auth", tags=["authentication"])

# Include SSO router
router.include_router(sso_router)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        user_repository: User repository
        
    Returns:
        The created user
        
    Raises:
        HTTPException: If a user with the same email already exists
    """
    # Check if user already exists
    existing_user = await user_repository.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())
    
    user_in_db = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    user = await user_repository.create_user(user_in_db)
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        created_at=user["created_at"]
    )


@router.post("/login", response_model=Token)
@limit_login_attempts(settings.LOGIN_RATE_LIMIT)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Authenticate a user and return JWT tokens.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        user_repository: User repository
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Get user by email
    user = await user_repository.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login/email", response_model=Token)
@limit_login_attempts(settings.LOGIN_RATE_LIMIT)
async def login_with_email(
    user_data: UserLogin,
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Authenticate a user with email and password and return JWT tokens.
    
    Args:
        user_data: User login data with email and password
        user_repository: User repository
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Get user by email
    user = await user_repository.get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    user_repository: UserRepository = Depends(get_user_repository)
):
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token: The refresh token
        user_repository: User repository
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    try:
        # Decode the refresh token
        token_payload = decode_token(refresh_token)
        
        # Check if it's a refresh token
        if token_payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = token_payload.sub
        
        # Get user from database
        user = await user_repository.get_user_by_id(user_id)
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
        
        # Create new tokens
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        created_at=current_user["created_at"]
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user = Depends(get_current_user)
):
    """
    Logout the current user by revoking their access token.
    
    Args:
        token: JWT token from the Authorization header
        current_user: The current authenticated user
        
    Returns:
        Success message
    """
    # Revoke the current token
    success = revoke_token(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke token"
        )
    
    return {"detail": "Successfully logged out"}


@router.post("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all_sessions(current_user = Depends(get_current_user)):
    """
    Logout from all sessions by revoking all tokens for the current user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Success message
    """
    # Revoke all tokens for the current user
    success = revoke_all_user_tokens(current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke all tokens"
        )
    
    return {"detail": "Successfully logged out from all sessions"}


@router.post("/revoke/{user_id}", status_code=status.HTTP_200_OK)
async def admin_revoke_user_tokens(
    user_id: str,
    current_user = Depends(get_current_user)
):
    """
    Admin endpoint to revoke all tokens for a specific user.
    
    Args:
        user_id: ID of the user whose tokens should be revoked
        current_user: The current authenticated admin user
        
    Returns:
        Success message
    """
    # Check if current user is an admin (you may need to adjust this based on your user model)
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    
    # Revoke all tokens for the specified user
    success = revoke_all_user_tokens(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke user tokens"
        )
    
    return {"detail": f"Successfully revoked all tokens for user {user_id}"}
