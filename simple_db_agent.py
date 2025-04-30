#!/usr/bin/env python3
# simple_db_agent.py - Un agente de base de datos simplificado

import os
import sys
import argparse
import json
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

def load_mysql_params():
    """Carga parámetros MySQL desde el archivo .env"""
    load_dotenv()
    
    params = {
        'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', '')
    }
    
    return params

def connect_to_mysql(params):
    """Establece conexión a MySQL con los parámetros dados"""
    try:
        # Mostrar parámetros (ocultando contraseña)
        safe_params = params.copy()
        safe_params['password'] = '********' if params['password'] else '[vacío]'
        print(f"🔌 Conectando a MySQL con: {safe_params}")
        
        connection = mysql.connector.connect(**params)
        
        if connection.is_connected():
            print("✅ Conexión exitosa a MySQL")
            return connection
    except Error as e:
        print(f"❌ Error al conectar: {e}")
    
    return None

def execute_query(connection, query):
    """Ejecuta una consulta SQL y devuelve los resultados"""
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
            results = cursor.fetchall()
            cursor.close()
            return results
        else:
            connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return [{"affected_rows": affected}]
    except Error as e:
        print(f"❌ Error al ejecutar consulta: {e}")
        return []

def generate_sql(prompt, provider):
    """Genera SQL a partir de lenguaje natural usando el proveedor de LLM"""
    prompt_template = f"""
    Genera una consulta SQL para MySQL basada en la siguiente solicitud en lenguaje natural:
    
    "{prompt}"
    
    Devuelve ÚNICAMENTE el SQL sin explicaciones adicionales.
    """
    
    try:
        sql = provider.generate_text(prompt_template)
        
        # Limpiar cualquier texto adicional alrededor del SQL
        sql = sql.strip()
        if sql.startswith('```sql'):
            sql = sql.split('```sql')[1]
        if sql.endswith('```'):
            sql = sql.split('```')[0]
        
        return sql.strip()
    except Exception as e:
        print(f"❌ Error al generar SQL: {e}")
        return None

def explain_results(results, prompt, sql, provider):
    """Genera una explicación de los resultados usando el proveedor de LLM"""
    explanation_prompt = f"""
    Explica los siguientes resultados de base de datos:
    
    Consulta original: "{prompt}"
    
    Consulta SQL: {sql}
    
    Resultados: {json.dumps(results, default=str)}
    
    Proporciona una explicación clara y concisa.
    """
    
    try:
        explanation = provider.generate_text(explanation_prompt)
        return explanation
    except Exception as e:
        print(f"❌ Error al generar explicación: {e}")
        return "No se pudo generar una explicación."

def interactive_mode(provider):
    """Ejecuta el agente en modo interactivo"""
    print("\n🤖 Modo interactivo del Agente de DB simplificado. Escribe 'salir' para terminar.\n")
    
    # Conectar a MySQL
    params = load_mysql_params()
    connection = connect_to_mysql(params)
    
    if not connection:
        print("❌ No se pudo establecer conexión a MySQL")
        return
    
    while True:
        prompt = input("\n🔍 Consulta: ")
        
        if prompt.lower() in ['salir', 'exit', 'quit']:
            print("👋 ¡Hasta luego!")
            connection.close()
            break
        
        # Generar SQL
        sql = generate_sql(prompt, provider)
        if not sql:
            print("❌ No se pudo generar SQL")
            continue
        
        print(f"\n✅ Consulta SQL generada:\n{sql}")
        
        # Ejecutar SQL
        results = execute_query(connection, sql)
        
        # Mostrar resultados
        print("\n📊 Resultados:")
        if results:
            try:
                import pandas as pd
                if isinstance(results[0], dict):
                    df = pd.DataFrame(results)
                else:
                    df = pd.DataFrame(results)
                print(df)
            except Exception:
                print(json.dumps(results, indent=2, default=str))
        else:
            print("Sin resultados")
        
        # Generar explicación
        explanation = explain_results(results, prompt, sql, provider)
        print(f"\n🧠 Explicación:\n{explanation}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Agente de DB simplificado")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
    parser.add_argument("--prompt", type=str, help="Consulta en lenguaje natural")
    
    args = parser.parse_args()
    
    # Cargar ProviderManager
    try:
        from providers.provider_manager import ProviderManager
        manager = ProviderManager("config/settings.yaml")
        provider = manager.get_provider()
        
        if args.interactive:
            interactive_mode(provider)
        elif args.prompt:
            # Modo de consulta única
            params = load_mysql_params()
            connection = connect_to_mysql(params)
            
            if not connection:
                print("❌ No se pudo establecer conexión a MySQL")
                return
            
            # Generar SQL
            sql = generate_sql(args.prompt, provider)
            if not sql:
                print("❌ No se pudo generar SQL")
                return
            
            print(f"\n✅ Consulta SQL generada:\n{sql}")
            
            # Ejecutar SQL
            results = execute_query(connection, sql)
            
            # Mostrar resultados
            print("\n📊 Resultados:")
            print(json.dumps(results, indent=2, default=str))
            
            # Generar explicación
            explanation = explain_results(results, args.prompt, sql, provider)
            print(f"\n🧠 Explicación:\n{explanation}")
            
            connection.close()
        else:
            print("❌ Se requiere --interactive o --prompt")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()