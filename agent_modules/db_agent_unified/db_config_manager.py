#!/usr/bin/env python3
# db_config_manager.py
"""
Database Configuration Manager

This script detects database systems on the machine, validates database connections,
and manages database configuration settings. It works both as a standalone script
and as an importable module.

Usage as script:
    python db_config_manager.py

Usage as module:
    from db_config_manager import get_db_info
    db_info = get_db_info()
"""

import os
import sys
import json
import socket
import platform
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv, set_key, find_dotenv

class DBConfigManager:
    """Database configuration detection and management."""
    
    def __init__(self, env_path=None, output_dir=None):
        """Initialize with paths for config and output."""
        # Find project root (where .env is located)
        self.env_path = env_path or find_dotenv(usecwd=True) or ".env"

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set output directory relative to this script's location
        if output_dir:
            # If absolute path is provided, use it
            if os.path.isabs(output_dir):
                self.output_dir = output_dir
            else:
                # Otherwise, make it relative to script directory
                self.output_dir = os.path.join(script_dir, output_dir)
        else:
            # Default: create data/db_info subdirectory in script's directory
            self.output_dir = os.path.join(script_dir, "data", "db_info")

        self.system_info = self._detect_all()
        
    def _detect_database_systems(self) -> Dict[str, Any]:
        """Detect available database systems, clients, and ports."""
        detected_systems = {}
        
        # Check for MySQL
        try:
            import mysql.connector
            mysql_available = True
        except ImportError:
            mysql_available = False
            
        if mysql_available:
            mysql_ports = self._scan_ports(['3306', '3307', '3308'])
            detected_systems["mysql"] = {
                "client_available": True,
                "ports_detected": mysql_ports,
                "status": "fully_available" if mysql_ports else "client_only"
            }
        
        # Check for PostgreSQL
        try:
            import psycopg2
            postgres_available = True
        except ImportError:
            postgres_available = False
            
        if postgres_available:
            postgres_ports = self._scan_ports(['5432', '5433'])
            detected_systems["postgresql"] = {
                "client_available": True,
                "ports_detected": postgres_ports,
                "status": "fully_available" if postgres_ports else "client_only"
            }
            
        # Check for SQLite (always available in Python)
        try:
            import sqlite3
            sqlite_available = True
        except ImportError:
            sqlite_available = False
            
        if sqlite_available:
            detected_systems["sqlite"] = {
                "client_available": True,
                "ports_detected": [],  # SQLite is file-based, no ports
                "status": "client_only"  # Always client only for SQLite
            }
            
        return detected_systems
    
    def _scan_ports(self, ports: List[str]) -> List[int]:
        """Scan if ports are open on localhost."""
        open_ports = []
        for port in ports:
            try:
                port_num = int(port)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    result = s.connect_ex(('127.0.0.1', port_num))
                    if result == 0:  # Port is open
                        open_ports.append(port_num)
            except:
                continue
                
        return open_ports
    
    def _load_env_variables(self) -> Dict[str, str]:
        """Load database configuration from .env file."""
        load_dotenv(self.env_path)
        env_vars = {}
        
        # Load MySQL config if exists
        mysql_config = {}
        if os.getenv('MYSQL_HOST'):
            mysql_config['host'] = os.getenv('MYSQL_HOST')
        if os.getenv('MYSQL_PORT'):
            mysql_config['port'] = int(os.getenv('MYSQL_PORT'))
        if os.getenv('MYSQL_USER'):
            mysql_config['user'] = os.getenv('MYSQL_USER')
        if os.getenv('MYSQL_PASSWORD') is not None:  # Allow empty password
            mysql_config['password'] = os.getenv('MYSQL_PASSWORD')
        if os.getenv('MYSQL_DATABASE'):
            mysql_config['database'] = os.getenv('MYSQL_DATABASE')
            
        if mysql_config:
            env_vars['mysql'] = mysql_config
            
        # Load PostgreSQL config if exists
        pg_config = {}
        if os.getenv('POSTGRES_HOST'):
            pg_config['host'] = os.getenv('POSTGRES_HOST')
        if os.getenv('POSTGRES_PORT'):
            pg_config['port'] = int(os.getenv('POSTGRES_PORT'))
        if os.getenv('POSTGRES_USER'):
            pg_config['user'] = os.getenv('POSTGRES_USER')
        if os.getenv('POSTGRES_PASSWORD') is not None:
            pg_config['password'] = os.getenv('POSTGRES_PASSWORD')
        if os.getenv('POSTGRES_DATABASE'):
            pg_config['database'] = os.getenv('POSTGRES_DATABASE')
            
        if pg_config:
            env_vars['postgresql'] = pg_config
            
        # Load SQLite config if exists
        sqlite_config = {}
        if os.getenv('SQLITE_DATABASE'):
            sqlite_config['database'] = os.getenv('SQLITE_DATABASE')
            
        if sqlite_config:
            env_vars['sqlite'] = sqlite_config
            
        return env_vars
    
    def _test_connection(self, db_type: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Test database connection with provided configuration."""
        if db_type.lower() == 'mysql':
            try:
                import mysql.connector
                conn_params = {}
                # Only include params that exist in the config
                if 'host' in params:
                    conn_params['host'] = params['host']
                if 'port' in params:
                    conn_params['port'] = int(params['port'])
                if 'user' in params:
                    conn_params['user'] = params['user'] 
                if 'password' in params:
                    conn_params['password'] = params['password']
                if 'database' in params:
                    conn_params['database'] = params['database']
                
                conn = mysql.connector.connect(**conn_params)
                if conn.is_connected():
                    server_info = conn.get_server_info()
                    conn.close()
                    return True, f"Connected to MySQL server version {server_info}"
                conn.close()
                return False, "Connection established but not active"
            except Exception as e:
                return False, str(e)
                
        elif db_type.lower() == 'postgresql':
            try:
                import psycopg2
                conn_params = {}
                # Only include params that exist in the config
                if 'host' in params:
                    conn_params['host'] = params['host']
                if 'port' in params:
                    conn_params['port'] = params['port']
                if 'user' in params:
                    conn_params['user'] = params['user']
                if 'password' in params:
                    conn_params['password'] = params['password']
                if 'database' in params:
                    conn_params['dbname'] = params['database']
                
                conn = psycopg2.connect(**conn_params)
                if conn.closed == 0:
                    version = conn.server_version
                    conn.close()
                    return True, f"Connected to PostgreSQL server version {version}"
                conn.close()
                return False, "Connection established but not active"
            except Exception as e:
                return False, str(e)
                
        elif db_type.lower() == 'sqlite':
            try:
                import sqlite3
                if 'database' not in params:
                    return False, "No database file specified"
                    
                db_path = params['database']
                if db_path != ':memory:' and not os.path.exists(db_path):
                    # For SQLite, if file doesn't exist, it will be created
                    # But we want to check if the directory exists
                    dir_path = os.path.dirname(db_path)
                    if dir_path and not os.path.exists(dir_path):
                        return False, f"Directory {dir_path} does not exist"
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()[0]
                conn.close()
                return True, f"Connected to SQLite version {version}"
            except Exception as e:
                return False, str(e)
                
        return False, f"Unsupported database type: {db_type}"
    
    def _request_credentials(self, db_type: str, existing_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Interactively request missing credentials."""
        config = existing_config or {}
        
        if db_type.lower() == 'mysql':
            print(f"\n🔧 MySQL Configuration")
            config['host'] = input(f"Host [{config.get('host', '127.0.0.1')}]: ") or config.get('host', '127.0.0.1')
            config['port'] = int(input(f"Port [{config.get('port', 3306)}]: ") or config.get('port', 3306))
            config['user'] = input(f"User [{config.get('user', 'root')}]: ") or config.get('user', 'root')
            config['password'] = input(f"Password [{config.get('password', '')}]: ") or config.get('password', '')
            config['database'] = input(f"Database [{config.get('database', '')}]: ") or config.get('database', '')
            
        elif db_type.lower() == 'postgresql':
            print(f"\n🔧 PostgreSQL Configuration")
            config['host'] = input(f"Host [{config.get('host', '127.0.0.1')}]: ") or config.get('host', '127.0.0.1')
            config['port'] = int(input(f"Port [{config.get('port', 5432)}]: ") or config.get('port', 5432))
            config['user'] = input(f"User [{config.get('user', 'postgres')}]: ") or config.get('user', 'postgres')
            config['password'] = input(f"Password [{config.get('password', '')}]: ") or config.get('password', '')
            config['database'] = input(f"Database [{config.get('database', '')}]: ") or config.get('database', '')
            
        elif db_type.lower() == 'sqlite':
            print(f"\n🔧 SQLite Configuration")
            default_db = config.get('database', ':memory:')
            config['database'] = input(f"Database path [{default_db}]: ") or default_db
            
        return config
    
    def _save_to_env(self, db_type: str, config: Dict[str, Any]) -> bool:
        """Save valid configuration to .env file."""
        try:
            if db_type.lower() == 'mysql':
                if 'host' in config:
                    set_key(self.env_path, "MYSQL_HOST", str(config['host']))
                if 'port' in config:
                    set_key(self.env_path, "MYSQL_PORT", str(config['port']))
                if 'user' in config:
                    set_key(self.env_path, "MYSQL_USER", str(config['user']))
                if 'password' in config:
                    set_key(self.env_path, "MYSQL_PASSWORD", str(config['password']))
                if 'database' in config:
                    set_key(self.env_path, "MYSQL_DATABASE", str(config['database']))
                    
            elif db_type.lower() == 'postgresql':
                if 'host' in config:
                    set_key(self.env_path, "POSTGRES_HOST", str(config['host']))
                if 'port' in config:
                    set_key(self.env_path, "POSTGRES_PORT", str(config['port']))
                if 'user' in config:
                    set_key(self.env_path, "POSTGRES_USER", str(config['user']))
                if 'password' in config:
                    set_key(self.env_path, "POSTGRES_PASSWORD", str(config['password']))
                if 'database' in config:
                    set_key(self.env_path, "POSTGRES_DATABASE", str(config['database']))
                    
            elif db_type.lower() == 'sqlite':
                if 'database' in config:
                    set_key(self.env_path, "SQLITE_DATABASE", str(config['database']))
                    
            return True
        except Exception as e:
            print(f"Error saving to .env: {e}")
            return False
    
    def _detect_all(self) -> Dict[str, Any]:
        """Run all detection processes and return complete system information."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Detect environment
        environment = {
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "in_docker": os.path.exists('/.dockerenv')
        }
        
        # Detect database systems
        db_systems = self._detect_database_systems()
        
        # Load configuration from .env
        env_configs = self._load_env_variables()
        
        # Test connections for configured databases
        valid_configs = {}
        for db_type, config in env_configs.items():
            if db_type in db_systems:
                valid, message = self._test_connection(db_type, config)
                if valid:
                    # Add status to the configuration
                    config_with_status = config.copy()
                    config_with_status["status"] = "configured"
                    config_with_status["connection_status"] = message
                    valid_configs[db_type] = config_with_status
                    
                    # Update database system status
                    db_systems[db_type]["configuration_valid"] = True
                else:
                    db_systems[db_type]["configuration_valid"] = False
                    db_systems[db_type]["connection_error"] = message
            
        # Assemble complete system information
        return {
            "timestamp": timestamp,
            "environment": environment,
            "database_systems": db_systems,
            "configuration": valid_configs
        }
    
    def save_system_info(self, filename: Optional[str] = None) -> str:
        """Save system information to a JSON file and return the filepath."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"db_system_info_{timestamp}.json"
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Save system info to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.system_info, f, indent=2)
        
        print(f"💾 System information saved to: {filepath}")
        return filepath
    
    def print_summary(self) -> None:
        """Print formatted summary of the system information."""
        info = self.system_info
        
        print("\n🔍 DATABASE SYSTEM DETECTION REPORT")
        print("==================================")
        print(f"🕒 Generated: {datetime.datetime.fromisoformat(info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print environment information
        print("\n📊 System Information:")
        for key, value in info['environment'].items():
            print(f"  {key.capitalize()}: {value}")
        
        # Print detected database systems
        print("\n📋 Detected Database Systems:")
        if info['database_systems']:
            for db_type, db_info in info['database_systems'].items():
                status_emoji = "✅" if db_info.get('status') == 'fully_available' else "⚠️"
                print(f"  {status_emoji} {db_type.upper()}:")
                print(f"     - Client available: {'Yes' if db_info.get('client_available') else 'No'}")
                
                if db_type.lower() != 'sqlite':
                    if db_info.get('ports_detected'):
                        ports_str = ', '.join(map(str, db_info.get('ports_detected', [])))
                        print(f"     - Server detected on port{'s' if len(db_info['ports_detected']) > 1 else ''}: {ports_str}")
                    else:
                        print(f"     - Server: Not detected")
                        
                print(f"     - Status: {db_info.get('status', 'Unknown')}")
                
                if 'configuration_valid' in db_info:
                    valid_str = "Valid" if db_info['configuration_valid'] else "Invalid"
                    print(f"     - Configuration: {valid_str}")
                    if not db_info['configuration_valid'] and 'connection_error' in db_info:
                        print(f"     - Error: {db_info['connection_error']}")
        else:
            print("  No database systems detected")
            
        # Print valid configurations
        if info.get('configuration'):
            print("\n💾 Valid Database Configurations:")
            for db_type, config in info['configuration'].items():
                print(f"  🔹 {db_type.upper()}:")
                # Hide password in display
                for key, value in config.items():
                    if key == 'password':
                        print(f"     - {key.capitalize()}: {'*' * len(str(value))}")
                    elif key not in ['status', 'connection_status']:
                        print(f"     - {key.capitalize()}: {value}")
                print(f"     - Status: {config.get('status', 'Unknown')}")
                if 'connection_status' in config:
                    print(f"     - Connection: {config['connection_status']}")
        else:
            print("\n💾 No valid database configurations found")
            
    def validate_configuration(self, db_type: str = "mysql") -> Tuple[bool, str]:
        """Validate configuration for specified database type."""
        env_configs = self._load_env_variables()
        
        if db_type.lower() not in env_configs:
            return False, f"No configuration found for {db_type}"
            
        config = env_configs[db_type.lower()]
        return self._test_connection(db_type, config)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Return the complete system information dictionary."""
        return self.system_info

def get_db_info() -> Dict[str, Any]:
    """Get database system information."""
    manager = DBConfigManager()
    manager.print_summary()
    return manager.get_system_info()

def main():
    """Main function when run as script."""
    try:
        manager = DBConfigManager()
        
        # Print system information
        manager.print_summary()
        
        # Save to file
        filepath = manager.save_system_info()
        print(f"\n✅ System information saved to: {filepath}")
        
        # Check if interactive mode is needed
        if len(sys.argv) > 1 and sys.argv[1] == "--configure":
            # Check existing configurations
            env_configs = manager._load_env_variables()
            
            # For each detected database system
            for db_type in manager.system_info['database_systems'].keys():
                valid = False
                
                # Check if configuration exists and is valid
                if db_type in env_configs:
                    valid, message = manager._test_connection(db_type, env_configs[db_type])
                    
                if not valid:
                    print(f"\n❌ {db_type.upper()} configuration is invalid or missing")
                    if input(f"Would you like to configure {db_type}? (y/n): ").lower() == 'y':
                        # Request credentials
                        config = manager._request_credentials(
                            db_type, 
                            env_configs.get(db_type, {})
                        )
                        
                        # Test connection
                        valid, message = manager._test_connection(db_type, config)
                        if valid:
                            print(f"✅ Connection successful: {message}")
                            # Save to .env
                            if manager._save_to_env(db_type, config):
                                print(f"✅ Configuration saved to {manager.env_path}")
                            else:
                                print(f"❌ Failed to save configuration")
                        else:
                            print(f"❌ Connection failed: {message}")
                            if input("Save this configuration anyway? (y/n): ").lower() == 'y':
                                if manager._save_to_env(db_type, config):
                                    print(f"✅ Configuration saved to {manager.env_path}")
                                else:
                                    print(f"❌ Failed to save configuration")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
