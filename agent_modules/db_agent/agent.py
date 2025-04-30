# agent_modules/db_agent/agent.py
from agent_modules.base_agent import BaseAgent
from providers.provider_manager import ProviderManager
from .db_connector import DBConnector
from .query_builder import QueryBuilder
from .db_connection_manager import DBConnectionManager
from typing import Dict, Any, List, Optional

class DBAgent(BaseAgent):
    def __init__(self, provider_manager: ProviderManager, **kwargs):
        super().__init__(provider_manager, name="DB Agent")
        self.description = "Agente para consulta de bases de datos mediante lenguaje natural"
        self.connection_manager = DBConnectionManager()
        self.connector = DBConnector()
        self.query_builder = QueryBuilder(self.provider_manager)
        self.capabilities = ["query_db", "explain_schema", "suggest_queries"]
        
    def run(self, input_data, **kwargs):
        """
        Ejecuta el agente con los datos de entrada proporcionados.
        Compatible con uso directo y con CrewAI.
        
        Args:
            input_data: Datos de entrada para el agente
                Si es dict: Procesamiento directo
                Si es str: Formato CrewAI (consulta en texto)
            **kwargs: Argumentos adicionales específicos del agente
            
        Returns:
            Dict con los resultados o str para formato CrewAI
        """
        # Determinar si los datos de entrada son para CrewAI o uso directo
        crew_mode = isinstance(input_data, str)
        
        if crew_mode:
            # Modo CrewAI: Convertir input_data a formato interno
            prompt = input_data
            db_connection = kwargs.get("connection", {})
            
            # Si no hay conexión especificada en kwargs, usar MySQL por defecto
            if not db_connection:
                db_connection = {"type": "mysql"}
                
            # Crear estructura de datos interna
            input_dict = {
                "prompt": prompt,
                "connection": db_connection
            }
        else:
            # Modo directo: Usar input_data como diccionario
            input_dict = input_data
            
        # Validar entrada
        if not self.validate_input(input_dict):
            error_response = {"error": "Input inválido"}
            return self._format_response(error_response, crew_mode)
            
        # Obtener datos del input
        prompt = input_dict.get("prompt", "")
        db_connection = input_dict.get("connection", {})
        
        # Determinar tipo de base de datos
        db_type = db_connection.get("type", "mysql").lower()
        
        # Verificar conexión con enfoque escalar
        success, message = self.connection_manager.connect(db_type, db_connection)
        
        if not success:
            error_response = {
                "error": f"No se pudo establecer conexión: {message}",
                "suggestion": "Verifique las credenciales e intente nuevamente"
            }
            return self._format_response(error_response, crew_mode)
            
        # Verificar mapeo de la base de datos
        if not self.connection_manager.verify_mapping(db_type):
            error_response = {
                "error": "No se pudo obtener la estructura de la base de datos",
                "suggestion": "Verifique los permisos y la conexión"
            }
            return self._format_response(error_response, crew_mode)
            
        # Obtener mapeo
        db_mapping = self.connection_manager.get_mapping(db_type)
        
        # Construir consulta SQL usando LLM
        sql_query = self.query_builder.build_query(prompt, db_connection, db_mapping)
        
        # Ejecutar consulta
        results = self.connection_manager.execute_query(db_type, sql_query)
        
        # Generar explicación
        explanation = self.query_builder.explain_query(sql_query, prompt)
        
        # Preparar respuesta
        response = {
            "query": sql_query,
            "results": results,
            "explanation": explanation
        }
        
        # Formatear según el modo
        return self._format_response(response, crew_mode)
    
    def _format_response(self, response: Dict[str, Any], crew_mode: bool) -> Any:
        """
        Formatea la respuesta según el modo de operación.
        
        Args:
            response: Respuesta a formatear
            crew_mode: True para formato CrewAI, False para formato diccionario
            
        Returns:
            Respuesta formateada (str para CrewAI, Dict para uso directo)
        """
        if not crew_mode:
            # Modo directo: devolver diccionario
            return response
            
        # Modo CrewAI: convertir a texto formateado
        import json
        
        if "error" in response:
            return f"ERROR: {response['error']}\nSugerencia: {response.get('suggestion', 'Intente con otra consulta')}"
            
        result_str = json.dumps(response.get('results', []), indent=2)
        
        formatted_response = f"""
Consulta SQL: {response.get('query', 'N/A')}

Resultados: {result_str}

Explicación: {response.get('explanation', 'N/A')}
"""
        return formatted_response.strip()
    
    def get_options(self):
        return [
            {"name": "connection", "type": "dict", "description": "Parámetros de conexión a la base de datos"},
            {"name": "prompt", "type": "string", "description": "Consulta en lenguaje natural"},
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida los datos de entrada para el agente.
        
        Args:
            input_data: Datos a validar
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        # Verificar que exista un prompt
        if "prompt" not in input_data or not input_data["prompt"]:
            return False
            
        # Verificar que exista información de conexión
        if "connection" not in input_data or not isinstance(input_data["connection"], dict):
            return False
            
        return True
        
    def for_crew_ai(self, task_description: str, **kwargs) -> str:
        """
        Punto de entrada específico para uso con CrewAI.
        
        Args:
            task_description: Descripción de la tarea (consulta)
            **kwargs: Parámetros adicionales
            
        Returns:
            Resultado formateado como texto
        """
        return self.run(task_description, **kwargs)


# Código para ejecución como script independiente
if __name__ == "__main__":
    import os
    import sys
    import json
    from pathlib import Path
    import argparse
    
    # Configurar la ruta para poder importar módulos del proyecto
    project_root = Path(__file__).resolve().parents[2]  # Sube dos niveles desde este archivo
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Importar lo necesario
    from providers.provider_manager import ProviderManager
    from dotenv import load_dotenv
    from utils.env_loader import load_env_variables

    # Cargar variables de entorno
    load_dotenv()
    
    # Mostrar variables de entorno para depuración
    env_vars = load_env_variables()
    print("🔍 Variables de entorno MySQL detectadas:")
    print(f"   - MYSQL_HOST: {env_vars.get('MYSQL_HOST', 'no definido')}")
    print(f"   - MYSQL_PORT: {env_vars.get('MYSQL_PORT', 'no definido')}")
    print(f"   - MYSQL_USER: {env_vars.get('MYSQL_USER', 'no definido')}")
    print(f"   - MYSQL_DATABASE: {env_vars.get('MYSQL_DATABASE', 'no definido')}")

    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Agente de consulta a bases de datos")
    parser.add_argument("--prompt", type=str, help="Consulta en lenguaje natural")
    parser.add_argument("--type", type=str, default="mysql", help="Tipo de base de datos (mysql, postgresql, sqlite)")
    parser.add_argument("--host", type=str, help="Host de la base de datos")
    parser.add_argument("--port", type=int, help="Puerto de la base de datos")
    parser.add_argument("--user", type=str, help="Usuario de la base de datos")
    parser.add_argument("--password", type=str, help="Contraseña de la base de datos")
    parser.add_argument("--database", type=str, help="Nombre de la base de datos")
    parser.add_argument("--config", type=str, default="config/settings.yaml", help="Ruta al archivo de configuración")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
    parser.add_argument("--reset-cache", action="store_true", help="Reiniciar caché de conexiones")
    parser.add_argument("--explore", action="store_true", help="Explorar bases de datos disponibles")
    
    args = parser.parse_args()

    try:
        # Inicializar ProviderManager
        config_path = os.path.join(project_root, args.config)
        if not os.path.exists(config_path):
            print(f"❌ Archivo de configuración no encontrado: {config_path}")
            sys.exit(1)
            
        print(f"🔍 Cargando configuración desde: {config_path}")
        manager = ProviderManager(config_path)
        
        # Inicializar el agente
        db_agent = DBAgent(provider_manager=manager)
        
        # Reiniciar caché si se solicita
        if args.reset_cache and hasattr(db_agent.connection_manager, 'clear_cache'):
            db_agent.connection_manager.clear_cache()
            print("🧹 Caché de conexiones reiniciado")
        
        # Modo exploración
        if args.explore:
            print("\n🔍 Explorando bases de datos disponibles en el sistema...\n")
            
            try:
                from utils.db_system_detector import run as detect_system
                system_info = detect_system()
                
                # Extraer información de bases de datos
                db_systems = system_info.get('database_systems', {})
                
                if not db_systems:
                    print("❌ No se detectaron sistemas de bases de datos en este equipo.")
                else:
                    print("✅ Sistemas de bases de datos detectados:")
                    
                    # Cargar variables de entorno para buscar hosts posibles
                    from utils.env_loader import load_env_variables
                    env_vars = load_env_variables()
                    
                    # Lista de hosts a probar para cada sistema
                    possible_hosts = {
                        'mysql': [
                            env_vars.get('MYSQL_HOST', ''),  # Primero probar lo que está en .env
                            '127.0.0.1',                     # Luego localhost
                            'localhost'                      # Nombre simbólico
                        ],
                        'postgresql': [
                            env_vars.get('POSTGRES_HOST', ''),
                            '127.0.0.1',
                            'localhost'
                        ],
                        'sqlite': [
                            None  # SQLite no necesita host
                        ]
                    }
                    
                    # Remover entradas vacías
                    for db_type in possible_hosts:
                        possible_hosts[db_type] = [h for h in possible_hosts[db_type] if h]
                        
                    for db_name, info in db_systems.items():
                        status = info.get('status', 'desconocido')
                        ports = info.get('ports_detected', [])
                        
                        status_emoji = "✅" if status == "fully_available" else "⚠️" if status == "client_only" else "❌"
                        
                        print(f"\n{status_emoji} {db_name.upper()}:")
                        print(f"   Estado: {status}")
                        print(f"   Cliente disponible: {'Sí' if info.get('client_available', False) else 'No'}")
                        
                        if ports:
                            print(f"   Puertos detectados: {', '.join(map(str, ports))}")
                        else:
                            print("   Puertos: No se detectaron servidores activos")
                        
                        # Intentar conexión solo si hay cliente disponible
                        if info.get('client_available', False):
                            # Para SQLite no necesitamos puertos
                            if db_name.lower() == 'sqlite':
                                # Intentar conectar a memoria
                                connection_params = {
                                    "type": "sqlite",
                                    "database": ":memory:"
                                }
                                success, message = db_agent.connection_manager.connect(db_name.lower(), connection_params)
                                print(f"   SQLite en memoria: {'✅ Disponible' if success else '❌ No disponible'}")
                            
                            # Para otras bases de datos, probar hosts y puertos
                            elif ports:
                                hosts_to_try = possible_hosts.get(db_name.lower(), ['127.0.0.1'])
                                connection_successful = False
                                
                                print(f"   Probando conexiones a {db_name.upper()}...")
                                
                                for host in hosts_to_try:
                                    for port in ports:
                                        print(f"   Intentando {host}:{port}...")
                                        
                                        # Preparar parámetros de conexión
                                        connection_params = {
                                            "type": db_name.lower(),
                                            "host": host,
                                            "port": port
                                        }
                                        
                                        # Añadir credenciales si existen en .env
                                        if db_name.lower() == 'mysql':
                                            if 'MYSQL_USER' in env_vars:
                                                connection_params['user'] = env_vars['MYSQL_USER']
                                            if 'MYSQL_PASSWORD' in env_vars:
                                                connection_params['password'] = env_vars['MYSQL_PASSWORD']
                                            if 'MYSQL_DATABASE' in env_vars:
                                                connection_params['database'] = env_vars['MYSQL_DATABASE']
                                        elif db_name.lower() == 'postgresql':
                                            if 'POSTGRES_USER' in env_vars:
                                                connection_params['user'] = env_vars['POSTGRES_USER']
                                            if 'POSTGRES_PASSWORD' in env_vars:
                                                connection_params['password'] = env_vars['POSTGRES_PASSWORD']
                                            if 'POSTGRES_DATABASE' in env_vars:
                                                connection_params['database'] = env_vars['POSTGRES_DATABASE']
                                        
                                        success, msg = db_agent.connection_manager.connect(
                                            db_name.lower(), connection_params
                                        )
                                        
                                        if success:
                                            connection_successful = True
                                            print(f"   ✅ Conexión exitosa a {host}:{port}")
                                            
                                            # Obtener lista de bases de datos
                                            try:
                                                results = db_agent.connection_manager.execute_query(
                                                    db_name.lower(), "SHOW DATABASES" if db_name.lower() == 'mysql' else 
                                                    "SELECT datname FROM pg_database WHERE datistemplate = false"
                                                )
                                                
                                                if results:
                                                    print("   📚 Bases de datos disponibles:")
                                                    for db in results:
                                                        print(f"      - {db[0]}")
                                            except Exception as e:
                                                print(f"   ⚠️ Conectado, pero sin permisos para listar bases de datos: {e}")
                                            
                                            # No necesitamos probar más hosts/puertos
                                            break
                                        else:
                                            print(f"   ❌ No se pudo conectar a {host}:{port} - {msg}")
                                            
                                    # Si ya encontramos una conexión exitosa, no probar más hosts
                                    if connection_successful:
                                        break
                                
                                if not connection_successful:
                                    print("   ⚠️ No se pudo establecer conexión con ninguna configuración")
                        
                    print("\n💡 Para usar una base de datos específica:")
                    print(f"   python -m agent_modules.db_agent.agent --interactive --type [{'|'.join(db_systems.keys())}]")
                    
            except Exception as e:
                print(f"❌ Error al explorar bases de datos: {e}")
                import traceback
                print(traceback.format_exc())
            
            sys.exit(0)
        
        # Modo interactivo o por línea de comandos
        if args.interactive:
            print("\n🤖 Modo interactivo del DBAgent. Escribe 'salir' para terminar.\n")
            
            while True:
                prompt = input("\n🔍 Consulta: ")
                
                if prompt.lower() in ["salir", "exit", "quit"]:
                    print("👋 ¡Hasta luego!")
                    break
                
                if prompt.lower() == "reset":
                    if hasattr(db_agent.connection_manager, 'clear_cache'):
                        db_agent.connection_manager.clear_cache()
                        print("🧹 Caché de conexiones reiniciado")
                    continue
                
                # Cargar variables de entorno para usar en la conexión
                env_vars = load_env_variables()
                
                # Preparar conexión utilizando solo el tipo y dejando que el escalamiento
                # del DBConnectionManager se encargue del resto
                connection = {
                    "type": args.type or "mysql",
                }
                
                # Añadir parámetros solo si están especificados explícitamente
                if args.host:
                    connection['host'] = args.host
                if args.port:
                    connection['port'] = args.port
                if args.user:
                    connection['user'] = args.user
                if args.password:
                    connection['password'] = args.password
                if args.database:
                    connection['database'] = args.database
                
                # Ejecutar consulta
                try:
                    result = db_agent.run({
                        "prompt": prompt,
                        "connection": connection
                    })
                    
                    # Mostrar resultados
                    if "error" in result:
                        print(f"\n❌ Error: {result['error']}")
                        if "suggestion" in result:
                            print(f"💡 Sugerencia: {result['suggestion']}")
                    else:
                        print(f"\n✅ Consulta SQL generada:\n{result['query']}")
                        print("\n📊 Resultados:")
                        
                        if result['results']:
                            # Intentar formatear resultados como tabla
                            try:
                                import pandas as pd
                                if isinstance(result['results'][0], dict):
                                    df = pd.DataFrame(result['results'])
                                else:
                                    df = pd.DataFrame(result['results'])
                                print(df)
                            except Exception as table_error:
                                print(json.dumps(result['results'], indent=2))
                        else:
                            print("Sin resultados")
                            
                        print(f"\n🧠 Explicación:\n{result['explanation']}")
                        
                except Exception as e:
                    print(f"❌ Error al procesar consulta: {e}")
                    
        else:
            # Modo línea de comandos
            if not args.prompt:
                print("❌ Se requiere un prompt. Use --prompt o --interactive")
                sys.exit(1)
                
            # Preparar conexión con argumentos
            connection = {
                "type": args.type or "mysql",
            }
            
            # Añadir parámetros solo si están especificados
            if args.host:
                connection['host'] = args.host
            if args.port:
                connection['port'] = args.port
            if args.user:
                connection['user'] = args.user
            if args.password:
                connection['password'] = args.password
            if args.database:
                connection['database'] = args.database
            
            # Ejecutar consulta
            result = db_agent.run({
                "prompt": args.prompt,
                "connection": connection
            })
            
            # Mostrar resultados en formato JSON
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)