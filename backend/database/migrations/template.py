"""
Template for database migration scripts.

Revision ID: ${revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic
revision = '${revision}'
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    Upgrade database schema to this revision.
    
    This function should contain the SQL commands to apply the migration.
    Example:
        op.create_table(
            'example_table',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Downgrade database schema from this revision.
    
    This function should contain the SQL commands to revert the migration.
    Example:
        op.drop_table('example_table')
    """
    ${downgrades if downgrades else "pass"}
