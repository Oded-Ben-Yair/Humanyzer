"""
Registry for available database migrations.
"""
import importlib
import logging
import os
from typing import Dict, List, Optional, Tuple

from alembic.script import ScriptDirectory
from alembic.config import Config

# Configure logging
logger = logging.getLogger(__name__)

class MigrationInfo:
    """Information about a migration."""
    
    def __init__(self, revision_id: str, description: str, path: str, dependencies: List[str] = None):
        """
        Initialize migration info.
        
        Args:
            revision_id: Unique identifier for the migration
            description: Human-readable description
            path: Path to the migration script
            dependencies: List of revision IDs this migration depends on
        """
        self.revision_id = revision_id
        self.description = description
        self.path = path
        self.dependencies = dependencies or []
    
    def __repr__(self) -> str:
        return f"<Migration {self.revision_id}: {self.description}>"


def get_available_migrations(alembic_cfg_path: Optional[str] = None) -> Dict[str, MigrationInfo]:
    """
    Get all available migrations from the Alembic scripts directory.
    
    Args:
        alembic_cfg_path: Path to alembic.ini file
        
    Returns:
        Dict[str, MigrationInfo]: Dictionary of available migrations
    """
    # Set up Alembic config
    if alembic_cfg_path is None:
        alembic_cfg_path = os.path.join(
            os.path.dirname(__file__), "../../../alembic.ini"
        )
    
    alembic_cfg = Config(alembic_cfg_path)
    script_directory = ScriptDirectory.from_config(alembic_cfg)
    
    # Get all revisions
    migrations = {}
    for revision in script_directory.walk_revisions():
        migration_info = MigrationInfo(
            revision_id=revision.revision,
            description=revision.doc,
            path=revision.path,
            dependencies=[revision.down_revision] if revision.down_revision else []
        )
        migrations[revision.revision] = migration_info
    
    return migrations


def resolve_dependencies(migrations: Dict[str, MigrationInfo]) -> List[str]:
    """
    Resolve migration dependencies to determine execution order.
    
    Args:
        migrations: Dictionary of available migrations
        
    Returns:
        List[str]: Ordered list of migration IDs to execute
    """
    # Simple topological sort
    visited = set()
    temp_visited = set()
    order = []
    
    def visit(migration_id: str):
        if migration_id in temp_visited:
            raise ValueError(f"Circular dependency detected in migrations: {migration_id}")
        
        if migration_id in visited:
            return
        
        temp_visited.add(migration_id)
        
        # Visit dependencies first
        for dep_id in migrations[migration_id].dependencies:
            if dep_id in migrations:
                visit(dep_id)
        
        temp_visited.remove(migration_id)
        visited.add(migration_id)
        order.append(migration_id)
    
    # Visit all migrations
    for migration_id in migrations:
        if migration_id not in visited:
            visit(migration_id)
    
    return order
