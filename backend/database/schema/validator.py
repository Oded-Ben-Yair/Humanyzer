"""
Database schema validation utility.
"""
import logging
from typing import Dict, List, Set, Tuple

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.engine import Engine

from ...db.db import engine
from .expectedSchema import get_expected_schema

# Configure logging
logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validates database schema against expected schema."""
    
    def __init__(self, engine: Engine = None):
        """
        Initialize schema validator.
        
        Args:
            engine: SQLAlchemy engine (uses default if None)
        """
        self.engine = engine or engine
        self.inspector = inspect(self.engine)
    
    def get_actual_schema(self) -> Dict[str, Dict]:
        """
        Get the actual database schema.
        
        Returns:
            Dict: Dictionary representing the actual schema
        """
        schema = {}
        
        # Get all table names
        table_names = self.inspector.get_table_names()
        
        for table_name in table_names:
            table_info = {
                'columns': {},
                'primary_key': [],
                'foreign_keys': [],
                'indexes': []
            }
            
            # Get columns
            columns = self.inspector.get_columns(table_name)
            for column in columns:
                col_name = column['name']
                table_info['columns'][col_name] = {
                    'type': str(column['type']),
                    'nullable': column.get('nullable', True),
                    'default': column.get('default', None)
                }
            
            # Get primary key
            pk = self.inspector.get_pk_constraint(table_name)
            table_info['primary_key'] = pk.get('constrained_columns', [])
            
            # Get foreign keys
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                table_info['foreign_keys'].append({
                    'columns': fk.get('constrained_columns', []),
                    'referred_table': fk.get('referred_table', ''),
                    'referred_columns': fk.get('referred_columns', [])
                })
            
            # Get indexes
            indexes = self.inspector.get_indexes(table_name)
            for index in indexes:
                table_info['indexes'].append({
                    'name': index.get('name', ''),
                    'columns': index.get('column_names', []),
                    'unique': index.get('unique', False)
                })
            
            schema[table_name] = table_info
        
        return schema
    
    def compare_schemas(self) -> Tuple[bool, List[str]]:
        """
        Compare actual schema with expected schema.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_differences)
        """
        actual_schema = self.get_actual_schema()
        expected_schema = get_expected_schema()
        
        differences = []
        is_valid = True
        
        # Check for missing tables
        expected_tables = set(expected_schema.keys())
        actual_tables = set(actual_schema.keys())
        
        missing_tables = expected_tables - actual_tables
        if missing_tables:
            is_valid = False
            differences.append(f"Missing tables: {', '.join(missing_tables)}")
        
        # Check for extra tables (not necessarily an error, but worth noting)
        extra_tables = actual_tables - expected_tables
        if extra_tables:
            differences.append(f"Extra tables (not in expected schema): {', '.join(extra_tables)}")
        
        # Check table structures for common tables
        common_tables = expected_tables.intersection(actual_tables)
        for table_name in common_tables:
            expected_table = expected_schema[table_name]
            actual_table = actual_schema[table_name]
            
            # Check columns
            expected_columns = set(expected_table['columns'].keys())
            actual_columns = set(actual_table['columns'].keys())
            
            missing_columns = expected_columns - actual_columns
            if missing_columns:
                is_valid = False
                differences.append(f"Table '{table_name}' missing columns: {', '.join(missing_columns)}")
            
            extra_columns = actual_columns - expected_columns
            if extra_columns:
                differences.append(f"Table '{table_name}' has extra columns: {', '.join(extra_columns)}")
            
            # Check column properties for common columns
            common_columns = expected_columns.intersection(actual_columns)
            for col_name in common_columns:
                expected_col = expected_table['columns'][col_name]
                actual_col = actual_table['columns'][col_name]
                
                # Check column type
                if expected_col['type'] != actual_col['type']:
                    is_valid = False
                    differences.append(
                        f"Column '{table_name}.{col_name}' type mismatch: "
                        f"expected {expected_col['type']}, got {actual_col['type']}"
                    )
                
                # Check nullability
                if expected_col['nullable'] != actual_col['nullable']:
                    is_valid = False
                    differences.append(
                        f"Column '{table_name}.{col_name}' nullability mismatch: "
                        f"expected {expected_col['nullable']}, got {actual_col['nullable']}"
                    )
            
            # Check primary key
            if set(expected_table['primary_key']) != set(actual_table['primary_key']):
                is_valid = False
                differences.append(
                    f"Table '{table_name}' primary key mismatch: "
                    f"expected {expected_table['primary_key']}, got {actual_table['primary_key']}"
                )
            
            # Check indexes (simplified check)
            expected_indexes = {idx['name']: set(idx['columns']) for idx in expected_table['indexes']}
            actual_indexes = {idx['name']: set(idx['columns']) for idx in actual_table['indexes']}
            
            for idx_name, idx_cols in expected_indexes.items():
                if idx_name not in actual_indexes:
                    is_valid = False
                    differences.append(f"Table '{table_name}' missing index: {idx_name}")
                elif idx_cols != actual_indexes[idx_name]:
                    is_valid = False
                    differences.append(
                        f"Table '{table_name}' index '{idx_name}' column mismatch: "
                        f"expected {idx_cols}, got {actual_indexes[idx_name]}"
                    )
        
        return is_valid, differences
    
    def validate(self) -> bool:
        """
        Validate the database schema.
        
        Returns:
            bool: True if schema is valid
        """
        is_valid, differences = self.compare_schemas()
        
        if not is_valid:
            logger.warning("Schema validation failed:")
            for diff in differences:
                logger.warning(f"  - {diff}")
        else:
            logger.info("Schema validation passed")
            if differences:
                logger.info("Non-critical differences found:")
                for diff in differences:
                    logger.info(f"  - {diff}")
        
        return is_valid
