"""
Database connection utilities.
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base # Changed from sqlalchemy.ext.declarative for newer SQLAlchemy versions
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file (if you have one)
# Ensure your .env file is in the root of your project (e.g., ~/Desktop/ExternalDrive/humanyzer/.env)
load_dotenv()

# Get the database URL from environment variable
# The guide (page 11) specifies: DATABASE_URL=postgresql://humanyze_user:humanyze_password@localhost:5432/humanyze_db
# For asyncpg, it should be: postgresql+asyncpg://humanyze_user:humanyze_password@localhost:5432/humanyze_db
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# If your DATABASE_URL from .env is in the synchronous format (postgresql://...)
# and you are using asyncpg, convert it.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# This is the SQLAlchemy declarative base. Your models will inherit from this.
Base = declarative_base()

# Create the asynchronous engine
# echo=True will log SQL queries, useful for debugging. Set to False in production.
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "AsyncSession" class
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get a database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Optional: commit if no exceptions
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close()

# Your MockAsyncSession can remain here if you use it for specific tests,
# but it should not be used by the main application logic or Alembic.
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
