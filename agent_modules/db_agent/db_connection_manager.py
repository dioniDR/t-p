# Versión mejorada de db_connection_manager.py
import os
from typing import Dict, Any, List, Optional, Tuple
from utils.db_system_detector import run as detect_system
from utils.env_loader import load_env_variables

class DBConnectionManager:
    """
    Gestor de conexiones a bases de datos con escalamiento automático.
    """
    
    def __init__(self):
        """Inicializa el gestor de conexiones."""
        self.connections = {}
        self.db_mappings = {}
        self.system_info = None
        self.env_vars = None
        
        # Inicializar detector de sistema
        self._initialize_system_detector()
        
        # Importar el conector solo cuando sea necesario
        from .db_connector import DBConnector
        self.connector = DBConnector()
    
    def _initialize_system_detector(self):
        """Inicializa el detector de sistema y carga variables de entorno."""
        print("🔍 Iniciando detección del sistema...")
        self.system_info = detect_system()
        print(f"🔍 Sistema detectado exitosamente")
        
        # Cargar variables de entorno
        self.env_vars = load_env_variables()
    
    def connect(self, db_type: str, custom_params: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Método principal para establecer conexión a la base de datos.
        Optimizado para reutilizar conexiones existentes.
        """
        # Normalizar el tipo de base de datos
        db_type = db_type.lower()
        
        # 1. Verificar si ya existe una conexión activa y validarla
        if db_type in self.connections and self.connections[db_type]['active']:
            # Verificar que la conexión sigue siendo válida
            try:
                # Realizar una consulta simple para verificar conexión
                if self.connector.is_connected(db_type):
                    print(f"✅ Reutilizando conexión existente a {db_type}")
                    return True, f"Reutilizando conexión existente a {db_type}"
                else:
                    print(f"⚠️ Conexión a {db_type} perdida, intentando reconectar")
            except Exception as e:
                print(f"⚠️ Error al verificar conexión existente: {e}")
                # Marcar la conexión como inactiva
                self.connections[db_type]['active'] = False
        
        # 2. Intentar con parámetros personalizados (mayor prioridad)
        if custom_params:
            print(f"🔍 Intentando conexión con parámetros personalizados")
            success, message = self._try_connection(db_type, custom_params)
            if success:
                return True, message
            print(f"⚠️ Conexión con parámetros personalizados falló: {message}")
        
        # 3. Intentar con variables de entorno
        env_params = self._get_env_params(db_type)
        if env_params:
            print(f"🔍 Intentando conexión con variables de entorno")
            success, message = self._try_connection(db_type, env_params)
            if success:
                return True, message
            print(f"⚠️ Conexión con variables de entorno falló: {message}")
        
        # 4. Intentar con sistema detectado
        sys_params = self._get_system_params(db_type)
        if sys_params:
            print(f"🔍 Intentando conexión con sistema detectado")
            success, message = self._try_connection(db_type, sys_params)
            if success:
                return True, message
            print(f"⚠️ Conexión con sistema detectado falló: {message}")
        
        # 5. Falló todo - sugerir solución
        return False, self._generate_failure_message(db_type)
    
    def _try_connection(self, db_type: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Intenta establecer una conexión con los parámetros dados.
        
        Args:
            db_type: Tipo de base de datos
            params: Parámetros de conexión
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Mostrar parámetros de conexión (ocultando contraseña)
        safe_params = params.copy()
        if 'password' in safe_params:
            safe_params['password'] = '********' if safe_params['password'] else '[vacío]'
        print(f"🔌 Intentando conectar a {db_type} con parámetros: {safe_params}")
        
        try:
            connection = self.connector.connect(db_type, params)
            
            if connection:
                # Guardar conexión exitosa
                self.connections[db_type] = {
                    'active': True,
                    'connection': connection,
                    'params': params
                }
                return True, f"Conexión exitosa a {db_type}"
            
            return False, "No se pudo establecer conexión"
        except Exception as e:
            return False, str(e)
    
    def _get_env_params(self, db_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene parámetros de conexión desde variables de entorno.
        
        Args:
            db_type: Tipo de base de datos
            
        Returns:
            Diccionario con parámetros o None
        """
        if not self.env_vars:
            return None
        
        params = {'type': db_type}
        
        if db_type == 'mysql':
            host = self.env_vars.get('MYSQL_HOST')
            port_str = self.env_vars.get('MYSQL_PORT')
            user = self.env_vars.get('MYSQL_USER')
            password = self.env_vars.get('MYSQL_PASSWORD')
            database = self.env_vars.get('MYSQL_DATABASE')
            
            if host:
                params['host'] = host
            if port_str:
                try:
                    params['port'] = int(port_str)
                except ValueError:
                    pass
            if user:
                params['user'] = user
            if password is not None:  # Permitir contraseña vacía
                params['password'] = password
            if database:
                params['database'] = database
                
            return params if 'host' in params and 'user' in params else None
            
        # Implementar para otros tipos de bases de datos
            
        return None
    
    def _get_system_params(self, db_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene parámetros de conexión desde la información del sistema.
        
        Args:
            db_type: Tipo de base de datos
            
        Returns:
            Diccionario con parámetros o None
        """
        if not self.system_info or 'database_systems' not in self.system_info:
            return None
        
        db_systems = self.system_info.get('database_systems', {})
        if db_type not in db_systems:
            return None
        
        db_info = db_systems[db_type]
        
        # Base mínima para parámetros
        params = {
            'type': db_type,
            'host': '127.0.0.1',
            'user': 'root' if db_type == 'mysql' else 'postgres',
            'password': ''
        }
        
        # Agregar puerto detectado si está disponible
        ports = db_info.get('ports_detected', [])
        if ports:
            params['port'] = ports[0]
        elif db_type == 'mysql':
            params['port'] = 3306
        elif db_type == 'postgresql':
            params['port'] = 5432
        
        return params
    
    def _generate_failure_message(self, db_type: str) -> str:
        """
        Genera un mensaje de error útil cuando fallan todas las conexiones.
        
        Args:
            db_type: Tipo de base de datos
            
        Returns:
            Mensaje de error con sugerencias
        """
        message = f"No se pudo establecer conexión a {db_type}.\n\n"
        message += "Por favor verifique:\n"
        message += "1. Que el servidor de base de datos esté en ejecución\n"
        
        if db_type == 'mysql':
            env_port = self.env_vars.get('MYSQL_PORT') if self.env_vars else None
            message += f"2. Que el puerto sea correcto (configurado: {env_port or 'no definido'})\n"
            message += "3. Que las credenciales en el archivo .env sean correctas\n"
        
        # Agregar información del sistema detectado
        if self.system_info and 'database_systems' in self.system_info:
            db_systems = self.system_info.get('database_systems', {})
            if db_type in db_systems:
                db_info = db_systems[db_type]
                ports = db_info.get('ports_detected', [])
                
                if ports:
                    message += f"\nSe detectaron puertos para {db_type}: {ports}\n"
                
                status = db_info.get('status', '')
                if status == 'client_only':
                    message += f"El cliente de {db_type} está instalado, pero no se detectó ningún servidor en ejecución.\n"
        
        message += "\nPuede verificar la conexión manualmente con un cliente de línea de comandos."
        
        return message
    
    # Métodos para el mapeo de la base de datos
    
    def verify_mapping(self, db_type: str) -> bool:
        """Verifica si existe un mapeo de la base de datos."""
        if db_type in self.db_mappings:
            return True
        
        # Si no hay mapeo pero hay conexión, generarlo
        if db_type in self.connections and self.connections[db_type]['active']:
            mapping = self._generate_mapping(db_type)
            if mapping:
                self.db_mappings[db_type] = mapping
                return True
        
        return False
    
    def _generate_mapping(self, db_type: str) -> Optional[Dict]:
        """Genera un mapeo de la estructura de la base de datos."""
        try:
            if db_type == 'mysql':
                # Consultas para obtener estructura de MySQL
                tables = self.connector.execute_query(db_type, "SHOW TABLES")
                
                mapping = {
                    'tables': {}
                }
                
                for table in tables:
                    table_name = table[0]
                    columns = self.connector.execute_query(db_type, f"DESCRIBE {table_name}")
                    mapping['tables'][table_name] = {
                        'columns': [col[0] for col in columns]
                    }
                
                return mapping
            
            # Implementar para otros tipos de bases de datos
        
        except Exception as e:
            print(f"❌ Error al generar mapeo para {db_type}: {str(e)}")
        
        return None
    
    def get_mapping(self, db_type: str) -> Optional[Dict]:
        """Obtiene el mapeo de una base de datos."""
        if self.verify_mapping(db_type):
            return self.db_mappings.get(db_type)
        return None
    
    def execute_query(self, db_type: str, query: str, params: Optional[List] = None) -> List:
        """
        Ejecuta una consulta SQL en la base de datos.
        
        Args:
            db_type: Tipo de base de datos
            query: Consulta SQL
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Lista de resultados
        """
        # Verificar conexión existente
        if db_type not in self.connections or not self.connections[db_type]['active']:
            success, message = self.connect(db_type)
            if not success:
                print(f"❌ No se pudo conectar a {db_type}: {message}")
                return []
        
        # Ejecutar consulta
        return self.connector.execute_query(db_type, query, params)
    
    def close(self, db_type: str = None):
        """
        Cierra conexiones de bases de datos.
        
        Args:
            db_type: Tipo de base de datos (si es None, cierra todas)
        """
        if db_type:
            if db_type in self.connections:
                self.connector.close(db_type)
                if db_type in self.connections:
                    del self.connections[db_type]
        else:
            # Cerrar todas las conexiones
            for db in list(self.connections.keys()):
                self.connector.close(db)
            self.connections = {}