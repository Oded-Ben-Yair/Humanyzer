"""
Database connection utilities.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Mock database session for testing
class MockAsyncSession:
    """Mock async session for testing."""
    
    async def __aenter__(self):
        """Enter the context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        pass
    
    async def commit(self):
        """Commit the transaction."""
        pass
    
    async def rollback(self):
        """Rollback the transaction."""
        pass
    
    async def close(self):
        """Close the session."""
        pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.
    
    Yields:
        Database session
    """
    session = MockAsyncSession()
    try:
        yield session
    finally:
        await session.close()
