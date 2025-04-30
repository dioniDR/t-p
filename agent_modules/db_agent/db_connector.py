# agent_modules/db_agent/db_connector.py
from typing import Dict, Any, List, Optional, Union

class DBConnector:
    """
    Conector para diferentes sistemas de bases de datos.
    Maneja las conexiones y ejecución de consultas.
    """
    
    def __init__(self):
        """Inicializa el conector de bases de datos."""
        self.connections = {}
    
    def connect(self, db_name: str, params: Dict[str, Any]) -> Any:
        """
        Establece una conexión a la base de datos.
        
        Args:
            db_name: Nombre/tipo de la base de datos
            params: Parámetros de conexión
            
        Returns:
            Objeto de conexión o None si falla
        """
        try:
            # Mostrar parámetros de conexión (ocultando contraseña)
            safe_params = params.copy()
            if 'password' in safe_params:
                safe_params['password'] = '********' if safe_params['password'] else '[vacío]'
            print(f"🔌 Conectando a {db_name} con parámetros: {safe_params}")
            
            if db_name.lower() == 'mysql':
                import mysql.connector
                # Crear diccionario de conexión con solo los parámetros necesarios
                conn_params = {
                    'host': params.get('host', '127.0.0.1'),
                    'port': int(params.get('port', 3306)),
                    'user': params.get('user', 'root'),
                    'password': params.get('password', '')
                }
                
                # Agregar base de datos si existe y no está vacía
                if 'database' in params and params['database']:
                    conn_params['database'] = params['database']
                
                connection = mysql.connector.connect(**conn_params)
                self.connections[db_name] = connection
                return connection
                
            # ... Código para otros sistemas de bases de datos ...
                
            else:
                print(f"❌ Tipo de base de datos no soportado: {db_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error al conectar a {db_name}: {str(e)}")
            return None
    
    def execute_query(self, db_name: str, query: str, params: Optional[List] = None) -> List:
        """
        Ejecuta una consulta SQL en la base de datos.
        
        Args:
            db_name: Nombre de la base de datos
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Lista con los resultados o lista vacía si hay error
        """
        if db_name not in self.connections:
            print(f"❌ No hay conexión activa a {db_name}")
            return []
            
        connection = self.connections[db_name]
        
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Verificar si la consulta devuelve resultados
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                connection.commit()
                affected = cursor.rowcount
                cursor.close()
                return [{"affected_rows": affected}]
                
        except Exception as e:
            print(f"❌ Error al ejecutar consulta en {db_name}: {str(e)}")
            return []
    
    def close(self, db_name: str) -> bool:
        """Cierra una conexión a base de datos."""
        if db_name in self.connections:
            try:
                self.connections[db_name].close()
                del self.connections[db_name]
                return True
            except Exception as e:
                print(f"❌ Error al cerrar conexión a {db_name}: {str(e)}")
                
        return False
    
    def close_all(self) -> None:
        """Cierra todas las conexiones activas."""
        for db_name in list(self.connections.keys()):
            self.close(db_name)
    
    def is_connected(self, db_name: str) -> bool:
        """
        Verifica si una conexión sigue activa.
        
        Args:
            db_name: Nombre de la base de datos
            
        Returns:
            True si la conexión está activa, False en caso contrario
        """
        if db_name not in self.connections:
            return False
            
        connection = self.connections[db_name]
        
        try:
            # Cada tipo de base de datos tiene su propia forma de verificar conexión
            if db_name.lower() == 'mysql':
                return connection.is_connected()
            elif db_name.lower() == 'postgresql':
                return not connection.closed
            elif db_name.lower() == 'sqlite':
                # SQLite siempre está conectado a menos que esté cerrado
                try:
                    # Intentar una consulta simple
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    return True
                except:
                    return False
                    
            return False
        except Exception:
            return False