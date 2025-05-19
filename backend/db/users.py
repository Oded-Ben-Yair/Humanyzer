
"""
Database operations for user management.
This module provides functions to create, retrieve, update, and delete users.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import json
from pathlib import Path

# Path to the users database file
DB_DIR = Path(os.getenv("DB_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")))
USERS_FILE = DB_DIR / "users.json"

# Ensure the data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Initialize users database if it doesn't exist
if not USERS_FILE.exists():
    with open(USERS_FILE, "w") as f:
        json.dump([], f)


async def _read_users() -> List[Dict[str, Any]]:
    """Read all users from the database."""
    with open(USERS_FILE, "r") as f:
        return json.load(f)


async def _write_users(users: List[Dict[str, Any]]) -> None:
    """Write users to the database."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, default=str)


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        The user if found, None otherwise
    """
    users = await _read_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email.
    
    Args:
        email: The user's email
        
    Returns:
        The user if found, None otherwise
    """
    users = await _read_users()
    for user in users:
        if user["email"] == email:
            return user
    return None


async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user.
    
    Args:
        user_data: User data to create
        
    Returns:
        The created user
    """
    users = await _read_users()
    
    # Ensure required fields
    if "id" not in user_data:
        user_data["id"] = str(uuid.uuid4())
    if "created_at" not in user_data:
        user_data["created_at"] = datetime.utcnow()
    if "updated_at" not in user_data:
        user_data["updated_at"] = datetime.utcnow()
    
    users.append(user_data)
    await _write_users(users)
    
    return user_data


async def update_user(user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a user.
    
    Args:
        user_id: The user ID
        user_data: User data to update
        
    Returns:
        The updated user if found, None otherwise
    """
    users = await _read_users()
    
    for i, user in enumerate(users):
        if user["id"] == user_id:
            # Update fields
            for key, value in user_data.items():
                user[key] = value
            
            # Update timestamp
            user["updated_at"] = datetime.utcnow()
            
            users[i] = user
            await _write_users(users)
            
            return user
    
    return None


async def delete_user(user_id: str) -> bool:
    """
    Delete a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        True if the user was deleted, False otherwise
    """
    users = await _read_users()
    
    for i, user in enumerate(users):
        if user["id"] == user_id:
            users.pop(i)
            await _write_users(users)
            return True
    
    return False


async def list_users() -> List[Dict[str, Any]]:
    """
    List all users.
    
    Returns:
        List of all users
    """
    return await _read_users()
