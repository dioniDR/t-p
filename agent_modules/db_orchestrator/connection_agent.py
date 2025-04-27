# 📚 agent_modules/db_orchestrator/connection_agent.py

import mysql.connector
import psycopg2
import sqlite3

class DBConnectionManager:
    """Clase para verificar conexiones a diferentes sistemas de bases de datos."""

    def check_mysql(self, env_vars):
        """Verifica conexión a MySQL usando las variables del entorno."""
        try:
            connection = mysql.connector.connect(
                host=env_vars.get("MYSQL_HOST", "127.0.0.1"),
                port=int(env_vars.get("MYSQL_PORT", 3306)),
                user=env_vars.get("MYSQL_USER", "root"),
                password=env_vars.get("MYSQL_PASSWORD", ""),
                database=env_vars.get("MYSQL_DATABASE", "")
            )
            connection.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_postgresql(self, env_vars):
        """Verifica conexión a PostgreSQL usando las variables del entorno."""
        try:
            connection = psycopg2.connect(
                host=env_vars.get("POSTGRES_HOST", "127.0.0.1"),
                port=int(env_vars.get("POSTGRES_PORT", 5432)),
                user=env_vars.get("POSTGRES_USER", "postgres"),
                password=env_vars.get("POSTGRES_PASSWORD", ""),
                dbname=env_vars.get("POSTGRES_DATABASE", "")
            )
            connection.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_sqlite(self, db_path=":memory:"):
        """Verifica conexión a una base de datos SQLite."""
        try:
            connection = sqlite3.connect(db_path)
            connection.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
