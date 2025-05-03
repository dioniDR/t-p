#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Generator

This script generates repository classes for database tables based on schema definitions.
It can be run as a standalone script or imported as a module.

Usage as script:
    python repository_generator.py --schema-path schemas/bodega_schemas.py --output-dir generated/bodega/repositories --db-name bodega

Usage as module:
    from crud_generator.repository_generator import generate_repositories
    generate_repositories("schemas/bodega_schemas.py", "generated/bodega/repositories", "bodega")
"""

import os
import sys
import importlib
import importlib.util
import inspect
from pathlib import Path
import re
from typing import Dict, List, Any, Tuple, Optional
import ast
import jinja2
from jinja2 import Environment, FileSystemLoader

class RepositoryGenerator:
    """Generator for repository classes based on database schemas."""
    
    def __init__(self, schema_path: str, output_dir: str, db_name: str):
        """
        Initialize the repository generator.
        
        Args:
            schema_path: Path to the schema definitions file
            output_dir: Directory where repositories will be generated
            db_name: Name of the database (used for naming)
        """
        self.schema_path = schema_path
        self.output_dir = output_dir
        self.db_name = db_name
        self.schemas = {}
        self.template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def load_schemas(self) -> Dict[str, Any]:
        """
        Load schema definitions from the schema file.
        
        Returns:
            Dictionary of schema objects by table name
        """
        # Get the absolute path to the schema file
        schema_path = os.path.abspath(self.schema_path)
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        # Import the schema module dynamically
        try:
            # Extract directory and filename
            module_dir = os.path.dirname(schema_path)
            module_file = os.path.basename(schema_path)
            module_name = os.path.splitext(module_file)[0]
            
            # Add the directory to path temporarily
            sys.path.insert(0, module_dir)
            
            # Import the module
            schemas_module = importlib.import_module(module_name)
            
            # Remove directory from path
            sys.path.pop(0)
            
            # Look for schema objects in the module
            schema_objects = {}
            for name, obj in schemas_module.__dict__.items():
                # Look for schema objects that match our naming convention
                if name.endswith('_schema') and isinstance(obj, object):
                    # Extract table name from schema variable name
                    table_name = name[:-7]  # Remove '_schema' suffix
                    schema_objects[table_name] = obj
            
            if not schema_objects:
                # If no schemas with _schema suffix, look for 'schemas' dictionary
                if hasattr(schemas_module, 'schemas') and isinstance(schemas_module.schemas, dict):
                    schema_objects = schemas_module.schemas
            
            self.schemas = schema_objects
            return schema_objects
            
        except Exception as e:
            raise ImportError(f"Failed to import schema module: {e}")
    
    def analyze_schema(self, table_name: str, schema_obj: Any) -> Dict[str, Any]:
        """
        Analyze a schema object to extract field information.
        
        Args:
            table_name: Name of the table
            schema_obj: Schema object to analyze
            
        Returns:
            Dictionary with table information
        """
        try:
            # Extract fields from schema object
            # This will depend on how your schema objects are structured
            fields = []
            primary_key = None
            
            # Example: If using Python Schema library
            if hasattr(schema_obj, 'schema'):
                schema_dict = schema_obj.schema
                
                # Analyze each field in the schema
                for field_name, field_validator in schema_dict.items():
                    # Skip optional fields for now
                    if str(field_validator).startswith('Optional'):
                        continue
                    
                    field_info = {
                        'name': field_name,
                        'type': self._determine_field_type(field_validator),
                        'nullable': False,
                        'primary_key': field_name.endswith('_id') and field_name.startswith(table_name)
                    }
                    
                    fields.append(field_info)
                    
                    # Identify primary key (typically table_name_id)
                    if field_info['primary_key']:
                        primary_key = field_name
            
            # Return structured information about the table
            return {
                'name': table_name,
                'fields': fields,
                'primary_key': primary_key,
                'schema_obj': schema_obj
            }
            
        except Exception as e:
            print(f"Error analyzing schema for {table_name}: {e}")
            return {
                'name': table_name,
                'fields': [],
                'primary_key': None,
                'schema_obj': schema_obj
            }
    
    def _determine_field_type(self, field_validator) -> str:
        """
        Determine Python type from schema field validator.
        
        Args:
            field_validator: Validator object from schema
            
        Returns:
            String representing Python type
        """
        validator_str = str(field_validator)
        
        if "str" in validator_str:
            return "str"
        elif "int" in validator_str:
            return "int"
        elif "float" in validator_str:
            return "float"
        elif "bool" in validator_str:
            return "bool"
        elif "date" in validator_str or "datetime" in validator_str:
            return "datetime.datetime"
        else:
            return "Any"
    
    def generate_repository(self, table_info: Dict[str, Any]) -> str:
        """
        Generate repository class code for a table.
        
        Args:
            table_info: Table information dictionary
            
        Returns:
            Generated Python code as string
        """
        # Load the repository template
        template = self.env.get_template("repository_template.py.jinja")
        
        # Render the template with table information
        rendered_code = template.render(
            table_name=table_info['name'],
            table_fields=table_info['fields'],
            primary_key=table_info['primary_key'],
            db_name=self.db_name,
            schema_name=f"{table_info['name']}_schema",
            schema_import=os.path.basename(self.schema_path).replace(".py", "")
        )
        
        return rendered_code
    
    def generate_base_repository(self) -> str:
        """
        Generate the base repository class that common functionality.
        
        Returns:
            Generated Python code for the base repository
        """
        # Load the base repository template
        template = self.env.get_template("base_repository_template.py.jinja")
        
        # Render the template
        rendered_code = template.render(
            db_name=self.db_name,
            schema_import=os.path.basename(self.schema_path).replace(".py", "")
        )
        
        return rendered_code
    
    def generate_init_file(self, table_names: List[str]) -> str:
        """
        Generate __init__.py file that exports all repositories.
        
        Args:
            table_names: List of table names
            
        Returns:
            Generated Python code for __init__.py
        """
        # Load the init file template
        template = self.env.get_template("init_template.py.jinja")
        
        # Render the template
        rendered_code = template.render(
            table_names=table_names,
            db_name=self.db_name
        )
        
        return rendered_code
    
    def save_repository(self, table_name: str, code: str) -> str:
        """
        Save generated repository code to a file.
        
        Args:
            table_name: Name of the table
            code: Generated code
            
        Returns:
            Path to the saved file
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define file path
        file_path = os.path.join(self.output_dir, f"{table_name}_repository.py")
        
        # Write code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def save_base_repository(self, code: str) -> str:
        """
        Save base repository code to a file.
        
        Args:
            code: Generated code
            
        Returns:
            Path to the saved file
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define file path
        file_path = os.path.join(self.output_dir, "base_repository.py")
        
        # Write code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def save_init_file(self, code: str) -> str:
        """
        Save __init__.py file.
        
        Args:
            code: Generated code
            
        Returns:
            Path to the saved file
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define file path
        file_path = os.path.join(self.output_dir, "__init__.py")
        
        # Write code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def generate_all(self) -> Dict[str, str]:
        """
        Generate all repository files.
        
        Returns:
            Dictionary mapping table names to file paths
        """
        # Load schemas
        schemas = self.load_schemas()
        
        if not schemas:
            print(f"No schemas found in {self.schema_path}")
            return {}
        
        # Generate files for each table
        generated_files = {}
        table_info_list = []
        
        for table_name, schema_obj in schemas.items():
            # Analyze schema
            table_info = self.analyze_schema(table_name, schema_obj)
            table_info_list.append(table_info)
            
            # Generate repository code
            repo_code = self.generate_repository(table_info)
            
            # Save repository file
            file_path = self.save_repository(table_name, repo_code)
            generated_files[table_name] = file_path
            
            print(f"Generated repository for {table_name}: {file_path}")
        
        # Generate and save base repository
        base_repo_code = self.generate_base_repository()
        base_repo_path = self.save_base_repository(base_repo_code)
        generated_files["base_repository"] = base_repo_path
        print(f"Generated base repository: {base_repo_path}")
        
        # Generate and save __init__.py
        init_code = self.generate_init_file([info['name'] for info in table_info_list])
        init_path = self.save_init_file(init_code)
        generated_files["__init__"] = init_path
        print(f"Generated __init__.py: {init_path}")
        
        return generated_files


def generate_repositories(schema_path: str, output_dir: str, db_name: str) -> Dict[str, str]:
    """
    Generate repository classes for all tables in a schema.
    
    Args:
        schema_path: Path to the schema definitions file
        output_dir: Directory where repositories will be generated
        db_name: Name of the database
        
    Returns:
        Dictionary mapping table names to generated file paths
    """
    generator = RepositoryGenerator(schema_path, output_dir, db_name)
    return generator.generate_all()


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate repository classes from schemas")
    parser.add_argument("--schema-path", required=True, help="Path to the schema definitions file")
    parser.add_argument("--output-dir", required=True, help="Directory where repositories will be generated")
    parser.add_argument("--db-name", required=True, help="Name of the database")
    
    args = parser.parse_args()
    
    # Generate repositories
    generate_repositories(args.schema_path, args.output_dir, args.db_name)
    
    print(f"\n✅ Repository generation complete for database: {args.db_name}")
    print(f"Output directory: {os.path.abspath(args.output_dir)}")