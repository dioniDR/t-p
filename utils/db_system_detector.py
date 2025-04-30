#!/usr/bin/env python3
# db_system_detector.py

import platform
import socket
import os
import json
from typing import Dict, List, Any
import sys
from datetime import datetime

class EnvironmentDetector:
    """Detecta información básica del entorno operativo de forma dinámica."""

    def __init__(self):
        """Inicializa el detector sin valores predefinidos."""
        self.environment_info = self._detect_environment()

    def _detect_environment(self) -> dict:
        """Detecta dinámicamente la información del entorno."""
        env_info = {}
        
        # Detección básica del sistema
        env_info["system"] = platform.system()
        env_info["release"] = platform.release()
        env_info["version"] = platform.version()
        env_info["architecture"] = platform.machine()
        
        # Intentar obtener el hostname
        try:
            env_info["hostname"] = platform.node()
        except:
            try:
                env_info["hostname"] = socket.gethostname()
            except:
                env_info["hostname"] = "unknown"
        
        # Detección de contenedor Docker
        env_info["in_docker"] = False
        if os.path.exists('/.dockerenv'):
            env_info["in_docker"] = True
        elif os.path.isfile('/proc/1/cgroup'):
            try:
                with open('/proc/1/cgroup', 'rt') as f:
                    env_info["in_docker"] = 'docker' in f.read()
            except:
                pass
        
        return env_info

    def get_environment_info(self) -> dict:
        """Retorna la información del entorno."""
        return self.environment_info


class DatabaseDetector:
    """Detecta sistemas de bases de datos dinámicamente."""
    
    def __init__(self):
        """Inicializa el detector de bases de datos."""
        self.db_systems = {}
        self.available_clients = self._detect_available_clients()
        self.open_ports = self._scan_common_db_ports()
        
    def _detect_available_clients(self) -> Dict[str, bool]:
        """Detecta qué clientes de bases de datos están disponibles."""
        clients = {}
        
        # Intentar importar MySQL
        try:
            import mysql.connector
            clients["mysql"] = True
        except ImportError:
            clients["mysql"] = False
            
        # Intentar importar PostgreSQL
        try:
            import psycopg2
            clients["postgresql"] = True
        except ImportError:
            clients["postgresql"] = False
            
        # Intentar importar SQLite
        try:
            import sqlite3
            clients["sqlite"] = True
        except ImportError:
            clients["sqlite"] = False

        # Intentar importar MongoDB
        try:
            import pymongo
            clients["mongodb"] = True
        except ImportError:
            clients["mongodb"] = False
            
        # Intentar importar Redis
        try:
            import redis
            clients["redis"] = True
        except ImportError:
            clients["redis"] = False
            
        return clients
    
    def _get_common_db_ports(self) -> Dict[str, List[int]]:
        """Retorna un diccionario con los puertos comunes para cada sistema."""
        return {
            "mysql": [3306, 3307, 3308, 3309],
            "postgresql": [5432, 5433, 5434],
            "mongodb": [27017, 27018, 27019],
            "redis": [6379, 6380],
            "cassandra": [9042, 9160],
            "elasticsearch": [9200, 9300],
            "mssql": [1433, 1434],
            "oracle": [1521, 1522]
        }
    
    def _scan_common_db_ports(self) -> Dict[str, List[int]]:
        """Escanea puertos comunes para bases de datos."""
        results = {}
        common_ports = self._get_common_db_ports()
        
        for db_type, ports in common_ports.items():
            open_ports = []
            for port in ports:
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                        open_ports.append(port)
                except:
                    continue
            
            # Solo incluir en resultados si hay puertos abiertos
            if open_ports:
                results[db_type] = open_ports
            
        return results
    
    def detect_database_systems(self) -> Dict[str, Any]:
        """Detecta dinámicamente solo los sistemas de bases de datos disponibles."""
        db_summary = {}
        
        # Combinar información de clientes disponibles y puertos abiertos
        for db_type in set(list(self.available_clients.keys()) + list(self.open_ports.keys())):
            client_available = self.available_clients.get(db_type, False)
            ports_detected = self.open_ports.get(db_type, [])
            
            # Solo incluir sistemas donde hay cliente o puertos detectados
            if client_available or ports_detected:
                if client_available and ports_detected:
                    status = "fully_available"
                elif client_available:
                    status = "client_only"
                else:
                    status = "ports_only"
                    
                db_summary[db_type] = {
                    "client_available": client_available,
                    "ports_detected": ports_detected,
                    "status": status
                }
        
        return db_summary


class SystemDetector:
    """Clase principal que coordina la detección completa del sistema."""
    
    def __init__(self):
        """Inicializa todos los detectores."""
        self.environment_detector = EnvironmentDetector()
        self.database_detector = DatabaseDetector()
        self.timestamp = datetime.now().isoformat()
    
    def detect_all(self) -> Dict[str, Any]:
        """Ejecuta todas las detecciones y genera un reporte completo."""
        # Detectar entorno
        environment_info = self.environment_detector.get_environment_info()
        
        # Detectar bases de datos
        database_info = self.database_detector.detect_database_systems()
        
        # Generar configuración dinámica basada en lo detectado
        config = self._generate_dynamic_config(environment_info, database_info)
        
        # Ensamblar el reporte completo
        return {
            "timestamp": self.timestamp,
            "environment": environment_info,
            "database_systems": database_info,
            "config": config
        }
    
    def _generate_dynamic_config(self, env_info, db_info) -> Dict[str, Any]:
        """Genera configuración dinámica basada en lo detectado."""
        config = {
            "retry_attempts": 3,
            "retry_delay_sec": 5,
            "monitor_interval_sec": 30
        }
        
        # Agregar puertos por defecto para bases de datos detectadas
        for db_type, info in db_info.items():
            if info["client_available"] or info["ports_detected"]:
                if db_type == "mysql":
                    config["default_mysql_port"] = info["ports_detected"][0] if info["ports_detected"] else 3306
                elif db_type == "postgresql":
                    config["default_postgresql_port"] = info["ports_detected"][0] if info["ports_detected"] else 5432
                elif db_type == "mongodb":
                    config["default_mongodb_port"] = info["ports_detected"][0] if info["ports_detected"] else 27017
                elif db_type == "redis":
                    config["default_redis_port"] = info["ports_detected"][0] if info["ports_detected"] else 6379
                elif db_type == "sqlite":
                    config["default_sqlite_memory"] = ":memory:"
        
        return config


def save_to_file(data, directory="./data/system_info", filename=None):
    """Guarda los datos en un archivo JSON."""
    # Crear directorio si no existe
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generar nombre de archivo con timestamp si no se proporciona
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_report_{timestamp}.json"
    
    # Ruta completa del archivo
    filepath = os.path.join(directory, filename)
    
    # Guardar datos en formato JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def print_summary(data):
    """Imprime un resumen formateado en la consola."""
    print("\n🎯 RESUMEN COMPLETO DEL SETUP\n")
    
    # Imprimir información del entorno
    print("🔵 Entorno operativo:")
    for key, value in data["environment"].items():
        print(f"   {key}: {value}")
    
    # Imprimir configuración
    print("\n🔵 Configuraciones activas:")
    for key, value in data["config"].items():
        print(f"   {key}: {value}")
    
    # Imprimir sistemas de bases de datos
    print("\n🔵 Sistemas de bases de datos detectados:")
    if data["database_systems"]:
        for db_name, info in data["database_systems"].items():
            print(f"\n   🔹 {db_name.upper()}")
            print(f"     - Cliente disponible: {'✅' if info['client_available'] else '❌'}")
            
            if info["ports_detected"]:
                print(f"     - Puertos detectados: {info['ports_detected']}")
            else:
                if db_name == "sqlite":
                    print(f"     - (No necesita puertos, funciona internamente)")
                else:
                    print(f"     - No se detectaron puertos activos.")
    else:
        print("   No se detectaron sistemas de bases de datos disponibles.")
    
    print("\n" + "="*50)


def run():
    """Función principal que ejecuta la detección completa."""
    try:
        # Iniciar detector
        detector = SystemDetector()
        
        # Ejecutar detección
        system_data = detector.detect_all()
        
        # Determinar si se ejecuta como script independiente o como módulo
        is_main = __name__ == "__main__"
        
        if is_main:
            # Guardar resultados
            filepath = save_to_file(system_data)
            
            # Imprimir resumen en consola
            print_summary(system_data)
            print(f"\n✅ Reporte completo guardado en: {filepath}")
        
        # Siempre devolver los datos para uso como módulo
        return system_data
    
    except Exception as e:
        error_msg = f"❌ Error durante la detección: {str(e)}"
        if __name__ == "__main__":
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            return {"error": error_msg, "traceback": traceback.format_exc()}
        else:
            return {"error": error_msg}


if __name__ == "__main__":
    run()