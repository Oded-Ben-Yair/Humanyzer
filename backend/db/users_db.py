"""
Database operations for user management using PostgreSQL.
This module provides functions to create, retrieve, update, and delete users.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: The user ID
        
    Returns:
        The user if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user:
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        }
    
    return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: The user's email
        
    Returns:
        The user if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if user:
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        }
    
    return None


async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_data: User data to create
        
    Returns:
        The created user
    """
    # Ensure required fields
    if "id" not in user_data:
        user_data["id"] = str(uuid.uuid4())
    
    # Create user object
    user = User(
        id=user_data.get("id"),
        email=user_data.get("email"),
        username=user_data.get("username"),
        hashed_password=user_data.get("hashed_password"),
        is_active=user_data.get("is_active", True)
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "hashed_password": user.hashed_password,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "is_active": user.is_active
    }


async def update_user(db: AsyncSession, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a user.
    
    Args:
        db: Database session
        user_id: The user ID
        user_data: User data to update
        
    Returns:
        The updated user if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Update fields
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "hashed_password": user.hashed_password,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "is_active": user.is_active
    }


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """
    Delete a user.
    
    Args:
        db: Database session
        user_id: The user ID
        
    Returns:
        True if the user was deleted, False otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True


async def list_users(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    List all users.
    
    Args:
        db: Database session
        
    Returns:
        List of all users
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        }
        for user in users
    ]
