#!/usr/bin/env python3
# db_connection_test.py
"""
Script simple para probar la conexión a MySQL leyendo variables desde .env
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

def load_env_variables():
    """Carga variables de entorno desde archivo .env"""
    load_dotenv()
    
    # Leer variables MySQL
    mysql_vars = {
        'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'port': os.getenv('MYSQL_PORT', '3306'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', '')
    }
    
    return mysql_vars

def test_connection(connection_params):
    """Prueba la conexión a MySQL con los parámetros proporcionados"""
    try:
        # Convertir puerto a entero
        if 'port' in connection_params:
            connection_params['port'] = int(connection_params['port'])
        
        # Mostrar parámetros de conexión (ocultando contraseña)
        safe_params = connection_params.copy()
        if 'password' in safe_params:
            safe_params['password'] = '********' if safe_params['password'] else '[vacío]'
        
        print("\n🔌 Intentando conexión a MySQL con los siguientes parámetros:")
        for key, value in safe_params.items():
            print(f"  - {key}: {value}")
        
        # Intentar conexión
        connection = mysql.connector.connect(**connection_params)
        
        if connection.is_connected():
            print("\n✅ Conexión exitosa a MySQL!")
            
            # Obtener información del servidor
            db_info = connection.get_server_info()
            print(f"  - Versión del servidor: {db_info}")
            
            # Mostrar base de datos actual
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"  - Base de datos actual: {db_name or '[Ninguna seleccionada]'}")
            
            # Mostrar bases de datos disponibles
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print("\n📚 Bases de datos disponibles:")
            for db in databases:
                print(f"  - {db[0]}")
                
            # Cerrar conexión
            cursor.close()
            connection.close()
            print("\n🔒 Conexión cerrada correctamente")
            return True
            
    except Error as e:
        print(f"\n❌ Error al conectar a MySQL: {e}")
        return False

def main():
    """Función principal"""
    print("\n🔍 Prueba de conexión a MySQL")
    print("============================")
    
    # Cargar variables desde .env
    mysql_params = load_env_variables()
    
    # Mostrar variables cargadas
    print("\n📋 Variables de entorno detectadas:")
    safe_params = mysql_params.copy()
    if 'password' in safe_params:
        safe_params['password'] = '********' if safe_params['password'] else '[vacío]'
    
    for key, value in safe_params.items():
        print(f"  - MYSQL_{key.upper()}: {value}")
    
    # Probar conexión
    success = test_connection(mysql_params)
    
    # Resultado final
    if success:
        print("\n✅ La prueba de conexión fue exitosa")
    else:
        print("\n❌ La prueba de conexión falló")
        
        # Sugerencias
        print("\n💡 Sugerencias:")
        print("  - Verifica que el servidor MySQL esté en ejecución")
        print("  - Confirma que el puerto es correcto")
        print("  - Asegúrate de que el usuario y contraseña son correctos")
        print("  - Verifica los permisos de conexión del usuario")

if __name__ == "__main__":
    main()