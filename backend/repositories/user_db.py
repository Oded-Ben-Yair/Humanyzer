"""
User repository for database operations.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

# Mock user database for testing
mock_users = {
    "1": {
        "id": "1",
        "email": "admin@humanyze.com",
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "is_active": True,
        "is_admin": True
    }
}

class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db_session: AsyncSession = None):
        """
        Initialize the repository.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        # First check mock_users
        user = mock_users.get(user_id)
        if user:
            return user
            
        # If not found, try to import and use the file-based users.py
        try:
            from backend.db.users import get_user_by_id as get_file_user
            return await get_file_user(user_id)
        except (ImportError, Exception):
            pass
            
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.
        
        Args:
            email: User email
            
        Returns:
            User data or None if not found
        """
        # First check mock_users
        for user in mock_users.values():
            if user["email"] == email:
                return user
                
        # If not found, try to import and use the file-based users.py
        try:
            from backend.db.users import get_user_by_email as get_file_user
            return await get_file_user(email)
        except (ImportError, Exception):
            pass
            
        return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            user_data: User data
            
        Returns:
            Created user data
        """
        user_id = user_data["id"]
        mock_users[user_id] = user_data
        return user_data
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a user.
        
        Args:
            user_id: User ID
            user_data: User data to update
            
        Returns:
            Updated user data or None if not found
        """
        if user_id not in mock_users:
            return None
        
        mock_users[user_id].update(user_data)
        return mock_users[user_id]
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        if user_id not in mock_users:
            return False
        
        del mock_users[user_id]
        return True
    
    async def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users.
        
        Returns:
            List of user data
        """
        return list(mock_users.values())
