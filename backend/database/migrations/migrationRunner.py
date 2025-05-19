"""
Migration execution engine for database schema changes.
"""
import logging
import os
from typing import List, Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from ...config import settings
from .migrationRegistry import get_available_migrations

# Configure logging
logger = logging.getLogger(__name__)

class MigrationRunner:
    """Handles execution of database migrations."""
    
    def __init__(self, alembic_cfg_path: str = None):
        """
        Initialize the migration runner.
        
        Args:
            alembic_cfg_path: Path to alembic.ini file
        """
        self.database_url = settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        
        # Set up Alembic config
        self.alembic_cfg_path = alembic_cfg_path or os.path.join(
            os.path.dirname(__file__), "../../../alembic.ini"
        )
        self.alembic_cfg = Config(self.alembic_cfg_path)
        
    def get_current_revision(self) -> Optional[str]:
        """
        Get the current migration revision from the database.
        
        Returns:
            str: Current revision identifier or None if no migrations applied
        """
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.warning(f"Could not connect to database: {str(e)}")
            logger.warning("Returning None as current revision")
            return None
    
    def get_pending_migrations(self) -> List[str]:
        """
        Get a list of pending migrations that need to be applied.
        
        Returns:
            List[str]: List of pending migration identifiers
        """
        try:
            current_revision = self.get_current_revision()
            script_directory = ScriptDirectory.from_config(self.alembic_cfg)
            
            # Get all revisions
            revisions = list(script_directory.walk_revisions())
            revision_ids = [rev.revision for rev in revisions]
            
            # If no migrations applied yet, all are pending
            if current_revision is None:
                return revision_ids
            
            # Find index of current revision
            try:
                current_index = revision_ids.index(current_revision)
                return revision_ids[:current_index]
            except ValueError:
                logger.warning(f"Current revision {current_revision} not found in available migrations")
                return []
        except Exception as e:
            logger.warning(f"Error getting pending migrations: {str(e)}")
            return []
    
    def run_migrations(self, target: str = "head") -> bool:
        """
        Run migrations to the specified target.
        
        Args:
            target: Target revision (default: "head" for latest)
            
        Returns:
            bool: True if migrations were successful
        """
        try:
            # Test database connection first
            with self.engine.connect() as connection:
                pass
                
            command.upgrade(self.alembic_cfg, target)
            logger.info(f"Successfully migrated database to {target}")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    def rollback(self, target: str) -> bool:
        """
        Rollback migrations to the specified target.
        
        Args:
            target: Target revision to rollback to
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            # Test database connection first
            with self.engine.connect() as connection:
                pass
                
            command.downgrade(self.alembic_cfg, target)
            logger.info(f"Successfully rolled back database to {target}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def create_migration(self, message: str, autogenerate: bool = True) -> Optional[str]:
        """
        Create a new migration script.
        
        Args:
            message: Migration message/description
            autogenerate: Whether to autogenerate migration based on models
            
        Returns:
            str: Path to the generated migration file or None if failed
        """
        try:
            if autogenerate:
                command.revision(self.alembic_cfg, message=message, autogenerate=True)
            else:
                command.revision(self.alembic_cfg, message=message)
            logger.info(f"Created new migration: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to create migration: {str(e)}")
            return False
    
    def validate_schema(self) -> bool:
        """
        Validate that the database schema matches the expected state.
        
        Returns:
            bool: True if schema is valid
        """
        # Get pending migrations
        pending = self.get_pending_migrations()
        if pending:
            logger.warning(f"Database schema validation failed: {len(pending)} pending migrations")
            return False
        
        logger.info("Database schema validation passed")
        return True
