# 📚 agent_modules/db_orchestrator/discovery_agent.py

# --------------------
# 🔵 Configuración de path raíz dinámico
# --------------------
import sys
import os

try:
    import pyprojroot
    project_root = pyprojroot.here()
except Exception:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

sys.path.insert(0, str(project_root))

# --------------------
# 🔵 Imports de módulos del proyecto
# --------------------
from utils.env_loader import load_env_variables
from agent_modules.db_orchestrator.connection_agent import DBConnectionManager
import platform

# --------------------
# 🔵 Definición del DiscoveryAgent
# --------------------
class DiscoveryAgent:
    """Agente de descubrimiento de bases de datos disponibles."""

    def __init__(self, config=None):
        self.config = config or {
            "retry_attempts": 3,
            "retry_delay_sec": 5,
            "default_mysql_port": 3306,
            "default_postgresql_port": 5432
        }
        self.environment_info = self.detect_environment()
        self.env_vars = load_env_variables()
        self.db_manager = DBConnectionManager()

    def detect_environment(self):
        """Detecta información básica del sistema operativo."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "in_docker": os.path.exists('/.dockerenv')
        }

    def discover(self):
        """Realiza la detección de sistemas de bases de datos activos."""
        report = {
            "environment": self.environment_info,
            "databases_detected": [],
            "errors": []
        }

        # Verificar MySQL
        mysql_status = self.db_manager.check_mysql(self.env_vars)
        if mysql_status["success"]:
            report["databases_detected"].append({"type": "MySQL", "status": "connected"})
        else:
            report["errors"].append({"type": "MySQL", "message": mysql_status.get("error", "Unknown error")})

        # Verificar PostgreSQL
        postgres_status = self.db_manager.check_postgresql(self.env_vars)
        if postgres_status["success"]:
            report["databases_detected"].append({"type": "PostgreSQL", "status": "connected"})
        else:
            report["errors"].append({"type": "PostgreSQL", "message": postgres_status.get("error", "Unknown error")})

        # Verificar SQLite
        sqlite_status = self.db_manager.check_sqlite()
        if sqlite_status["success"]:
            report["databases_detected"].append({"type": "SQLite", "status": "connected"})
        else:
            report["errors"].append({"type": "SQLite", "message": sqlite_status.get("error", "Unknown error")})

        return report

# --------------------
# 🔵 Modo ejecución directa (standalone)
# --------------------
if __name__ == "__main__":
    agent = DiscoveryAgent()
    summary = agent.discover()
    
    from pprint import pprint
    print("\n🎯 RESUMEN DEL DISCOVERY:")
    pprint(summary, sort_dicts=False)
