"""
Admin routes for database management.
"""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ...database.migrations.migrationRunner import MigrationRunner
from ...database.schema.validator import SchemaValidator
from ...auth.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/database", tags=["admin", "database"])

# Models
class MigrationStatus(BaseModel):
    """Migration status response model."""
    current: Optional[str]
    pending: List[str]

class SchemaValidationResult(BaseModel):
    """Schema validation response model."""
    valid: bool
    differences: List[str]

class CreateMigrationRequest(BaseModel):
    """Create migration request model."""
    message: str
    autogenerate: bool = True

class MigrationResponse(BaseModel):
    """Migration operation response model."""
    success: bool
    message: str

# Routes
@router.get("/migration-status", response_model=MigrationStatus)
async def get_migration_status(current_user=Depends(get_current_admin_user)):
    """
    Get the current migration status.
    
    Returns:
        MigrationStatus: Current migration status
    """
    try:
        runner = MigrationRunner()
        current = runner.get_current_revision()
        pending = runner.get_pending_migrations()
        
        return MigrationStatus(
            current=current,
            pending=pending
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get migration status: {str(e)}")

@router.get("/schema-validation", response_model=SchemaValidationResult)
async def validate_schema(current_user=Depends(get_current_admin_user)):
    """
    Validate the database schema.
    
    Returns:
        SchemaValidationResult: Schema validation result
    """
    try:
        validator = SchemaValidator()
        is_valid, differences = validator.compare_schemas()
        
        return SchemaValidationResult(
            valid=is_valid,
            differences=differences
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate schema: {str(e)}")

@router.post("/migrations", response_model=MigrationResponse)
async def create_migration(
    request: CreateMigrationRequest,
    current_user=Depends(get_current_admin_user)
):
    """
    Create a new migration.
    
    Args:
        request: Create migration request
        
    Returns:
        MigrationResponse: Operation result
    """
    try:
        runner = MigrationRunner()
        success = runner.create_migration(request.message, autogenerate=request.autogenerate)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create migration")
        
        return MigrationResponse(
            success=True,
            message=f"Successfully created migration: {request.message}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create migration: {str(e)}")

@router.post("/migrations/run", response_model=MigrationResponse)
async def run_migrations(
    background_tasks: BackgroundTasks,
    target: str = "head",
    current_user=Depends(get_current_admin_user)
):
    """
    Run pending migrations.
    
    Args:
        background_tasks: FastAPI background tasks
        target: Target revision (default: "head")
        
    Returns:
        MigrationResponse: Operation result
    """
    try:
        runner = MigrationRunner()
        
        # Run migrations in the background to avoid blocking the request
        def run_migrations_task():
            runner.run_migrations(target)
        
        background_tasks.add_task(run_migrations_task)
        
        return MigrationResponse(
            success=True,
            message=f"Migration to {target} started in the background"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run migrations: {str(e)}")

@router.post("/migrations/rollback/{target}", response_model=MigrationResponse)
async def rollback_migrations(
    target: str,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_admin_user)
):
    """
    Roll back migrations to the specified target.
    
    Args:
        target: Target revision to roll back to
        background_tasks: FastAPI background tasks
        
    Returns:
        MigrationResponse: Operation result
    """
    try:
        runner = MigrationRunner()
        
        # Run rollback in the background to avoid blocking the request
        def rollback_task():
            runner.rollback(target)
        
        background_tasks.add_task(rollback_task)
        
        return MigrationResponse(
            success=True,
            message=f"Rollback to {target} started in the background"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to roll back migrations: {str(e)}")
