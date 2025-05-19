#!/usr/bin/env python
"""
CLI tool for managing database migrations.
"""
import argparse
import logging
import os
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.database.migrations.migrationRunner import MigrationRunner
from backend.database.schema.validator import SchemaValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Database migration management tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration description")
    create_parser.add_argument(
        "--no-autogenerate", 
        action="store_true", 
        help="Don't autogenerate migration from models"
    )
    
    # Run migrations command
    run_parser = subparsers.add_parser("run", help="Run pending migrations")
    run_parser.add_argument(
        "--target", 
        default="head", 
        help="Target revision (default: head)"
    )
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument(
        "target", 
        help="Target revision to rollback to"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate database schema")
    
    return parser

def main():
    """Main entry point for the CLI tool."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize migration runner
    runner = MigrationRunner()
    
    if args.command == "create":
        # Create a new migration
        autogenerate = not args.no_autogenerate
        success = runner.create_migration(args.message, autogenerate=autogenerate)
        if not success:
            sys.exit(1)
    
    elif args.command == "run":
        # Run migrations
        success = runner.run_migrations(args.target)
        if not success:
            sys.exit(1)
    
    elif args.command == "rollback":
        # Rollback migrations
        success = runner.rollback(args.target)
        if not success:
            sys.exit(1)
    
    elif args.command == "status":
        # Show migration status
        current = runner.get_current_revision()
        pending = runner.get_pending_migrations()
        
        print(f"Current revision: {current or 'None'}")
        if pending:
            print(f"Pending migrations: {len(pending)}")
            for migration in pending:
                print(f"  - {migration}")
        else:
            print("No pending migrations")
    
    elif args.command == "validate":
        # Validate schema
        validator = SchemaValidator()
        is_valid = validator.validate()
        if not is_valid:
            sys.exit(1)

if __name__ == "__main__":
    main()
