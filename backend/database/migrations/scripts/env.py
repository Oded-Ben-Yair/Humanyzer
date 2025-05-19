"""
Alembic environment script.
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Import your SQLAlchemy Base
# This assumes 'Base' is correctly defined in backend/db/db.py
# (e.g., Base = declarative_base())
from backend.db.db import Base

# 2. !!! IMPORTANT: Import ALL your SQLAlchemy models here !!!
# Every model that inherits from 'Base' must be imported for Alembic
# to detect table creations, alterations, and deletions.
# If models are not imported, Base.metadata will not contain them.
# Example:
from backend.db.models import User
# If you have other models in backend.db.models or other files, import them too:
# from backend.db.models import Post, Comment # If they exist
# from backend.another_module import AnotherModel # If it exists

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Set your model's MetaData object for 'autogenerate' support.
# Alembic will compare this metadata against the database's current state.
target_metadata = Base.metadata

# 4. Configure the database URL for Alembic.
# This section attempts to use 'settings.DATABASE_URL' from 'backend.config'.
# IMPORTANT: For standard Alembic operation with engine_from_config,
# this URL should be a SYNCHRONOUS database URL
# (e.g., "postgresql://user:password@host/dbname")
# and NOT an asynchronous one (e.g., "postgresql+asyncpg://...").
try:
    from backend.config import settings
    db_url = settings.DATABASE_URL

    # If your application uses an async URL (e.g., "postgresql+asyncpg://...")
    # but Alembic needs a sync one, convert it.
    # (The .env from the guide: DATABASE_URL=postgresql://... is already sync)
    if db_url and "postgresql+asyncpg://" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    # Add similar replacements if you use other async drivers like +aiomysql, etc.

    if db_url:
        config.set_main_option("sqlalchemy.url", db_url)
    else:
        # Fallback if settings.DATABASE_URL is None or empty
        print("Warning: settings.DATABASE_URL from backend.config was empty or None. "
              "Alembic will rely on sqlalchemy.url in alembic.ini.")

except ImportError:
    # Fallback or error if backend.config.settings is not found
    print("Warning: Could not import 'settings' from 'backend.config'. "
          "Alembic will rely on sqlalchemy.url set in alembic.ini or environment.")
    # Ensure 'sqlalchemy.url' is properly set in your 'alembic.ini' if this happens.
    # For example, in alembic.ini:
    # sqlalchemy.url = postgresql://humanyze_user:humanyze_password@localhost:5432/humanyze_db
    # Or, using an environment variable (ensure this env var is set):
    # sqlalchemy.url = %(DATABASE_URL_SYNC)s

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError(
            "Database URL for Alembic is not configured for offline mode. "
            "Check sqlalchemy.url in alembic.ini or env.py settings."
        )
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # This uses the [alembic] section from alembic.ini by default
    # for configurations like sqlalchemy.url
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", # Looks for sqlalchemy.url, sqlalchemy.poolclass etc.
        poolclass=pool.NullPool, # Use NullPool for Alembic CLI operations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
            # You can add include_schemas=True if you use multiple schemas
            # and want Alembic to manage them.
            # process_revision_directives=your_custom_processor, # For advanced scenarios
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
