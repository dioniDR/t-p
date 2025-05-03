#!/usr/bin/env python3
"""
Database Schema Generator

This script connects to a database, reads its structure, and automatically
generates schema validation definitions for all tables.

It can be run as a standalone script or imported as a module.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import json
from typing import Dict, List, Any, Optional, Tuple

# Load environment variables
load_dotenv()

class SchemaGenerator:
    """Generates schema validation definitions from database structure."""
    
    def __init__(self, db_name: Optional[str] = None):
        """
        Initialize the schema generator.
        
        Args:
            db_name: Database name (default: from .env or 'bodega')
        """
        self.connection = None
        self.db_name = db_name or os.getenv('MYSQL_DATABASE', 'bodega')
        self.schemas = {}
        
    def connect(self) -> bool:
        """
        Connect to the database using .env credentials.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', '127.0.0.1'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=self.db_name
            )
            
            if self.connection.is_connected():
                print(f"✅ Connected to MySQL database: {self.db_name}")
                return True
            
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
        
        return False
    
    def get_tables(self) -> List[str]:
        """
        Get list of tables in the database.
        
        Returns:
            List of table names
        """
        if not self.connection or not self.connection.is_connected():
            print("❌ No active connection")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        except Error as e:
            print(f"❌ Error getting tables: {e}")
            return []
    
    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column definitions for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column definitions
        """
        if not self.connection or not self.connection.is_connected():
            print("❌ No active connection")
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            cursor.close()
            return columns
        except Error as e:
            print(f"❌ Error describing table {table_name}: {e}")
            return []
    
    def map_mysql_type_to_schema(self, mysql_type: str) -> str:
        """
        Map MySQL type to Python schema library type.
        
        Args:
            mysql_type: MySQL data type
            
        Returns:
            Python type string for schema validation
        """
        mysql_type = mysql_type.lower()
        
        # Extract base type if includes size, e.g., varchar(255) -> varchar
        base_type = mysql_type.split('(')[0].lower()
        
        # Map MySQL data types to Python types
        if base_type in ['varchar', 'char', 'text', 'longtext', 'enum']:
            return 'str'
        elif base_type in ['int', 'tinyint', 'smallint', 'mediumint', 'bigint']:
            return 'int'
        elif base_type in ['float', 'double', 'decimal']:
            return 'float'
        elif base_type in ['date', 'datetime', 'timestamp']:
            return 'str'  # Dates typically stored as strings
        elif base_type in ['boolean', 'bit']:
            return 'bool'
        elif base_type in ['json', 'blob', 'longblob']:
            return 'object'
        else:
            return 'object'  # Default fallback
    
    def generate_schema(self, table_name: str, columns: List[Dict[str, Any]]) -> str:
        """
        Generate schema validation code for a table.
        
        Args:
            table_name: Name of the table
            columns: Column definitions
            
        Returns:
            Schema definition code
        """
        schema_lines = [
            f"{table_name}_schema = Schema({{"
        ]
        
        for column in columns:
            field_name = column['Field']
            field_type = self.map_mysql_type_to_schema(column['Type'])
            nullable = column['Null'] == 'YES'
            
            # Generate field validation based on type and nullability
            if nullable:
                schema_lines.append(f"    Optional('{field_name}'): Or(None, {field_type}),")
            else:
                if field_type == 'str':
                    schema_lines.append(f"    '{field_name}': And({field_type}, len),")
                elif field_type == 'int':
                    schema_lines.append(f"    '{field_name}': {field_type},")
                elif field_type == 'float':
                    schema_lines.append(f"    '{field_name}': {field_type},")
                else:
                    schema_lines.append(f"    '{field_name}': {field_type},")
        
        schema_lines.append("})")
        
        return "\n".join(schema_lines)
    
    def generate_all_schemas(self) -> str:
        """
        Generate schema validation code for all tables.
        
        Returns:
            Complete schema file content
        """
        if not self.connect():
            return "# Failed to connect to database"
        
        tables = self.get_tables()
        if not tables:
            return "# No tables found"
        
        schema_file = [
            "# Auto-generated schema validation for database: " + self.db_name,
            "from schema import Schema, And, Or, Use, Optional\n"
        ]
        
        for table in tables:
            print(f"🔍 Analyzing table: {table}")
            columns = self.get_table_structure(table)
            
            # Store schema definition for this table
            table_schema = self.generate_schema(table, columns)
            self.schemas[table] = table_schema
            
            schema_file.append("\n# Schema for table: " + table)
            schema_file.append(table_schema)
        
        schema_file.append("\n# Export all schemas")
        schema_file.append("schemas = {")
        for table in tables:
            schema_file.append(f"    '{table}': {table}_schema,")
        schema_file.append("}")
        
        # Close connection
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Connection closed")
        
        return "\n".join(schema_file)
    
    def save_schemas(self, directory: str = "schemas") -> str:
        """
        Save generated schemas to a file in the same directory as this script.
        
        Args:
            directory: Directory to save schema file (relative to script directory)
            
        Returns:
            Path to the saved file
        """
        schema_content = self.generate_all_schemas()
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create target directory path
        target_dir = os.path.join(script_dir, directory)
        
        # Create directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Create filename based on database name
        filename = f"{self.db_name}_schemas.py"
        filepath = os.path.join(target_dir, filename)
        
        # Write schema to file
        with open(filepath, 'w') as f:
            f.write(schema_content)
        
        print(f"✅ Schema file saved to: {filepath}")
        return filepath
    
    def get_schemas(self) -> Dict[str, str]:
        """
        Get generated schemas (after generation).
        
        Returns:
            Dictionary of table names and their schema definitions
        """
        return self.schemas

def main():
    """Main function when run as script."""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate schema validations from database structure")
    parser.add_argument('--db', type=str, help='Database name (default: from .env or "bodega")')
    parser.add_argument('--output', type=str, default='schemas', help='Output directory for schema file')
    args = parser.parse_args()
    
    # Generate schemas
    generator = SchemaGenerator(db_name=args.db)
    filepath = generator.save_schemas(directory=args.output)
    
    print(f"\n✨ Schema generation complete!")
    print(f"Generated schema validations for database: {generator.db_name}")
    print(f"Schema file saved to: {filepath}")
    
    return 0

# Allow running as a script or importing as a module
if __name__ == "__main__":
    sys.exit(main())