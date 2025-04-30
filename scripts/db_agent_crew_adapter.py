# scripts/db_agent_crew_adapter.py
import os
import sys
from pathlib import Path
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Añadir el directorio raíz al path para poder importar módulos del proyecto
project_root = Path(__file__).resolve().parents[1]  # Sube un nivel desde scripts/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

# Importar componentes necesarios
from providers.provider_manager import ProviderManager
from agent_modules.db_agent.agent import DBAgent

def create_db_agent_for_crew(config_path="config/settings.yaml", provider_name=None):
    """
    Crea un agente DB adaptado para CrewAI.
    
    Args:
        config_path: Ruta al archivo de configuración
        provider_name: Nombre del proveedor a utilizar (opcional)
        
    Returns:
        Agente CrewAI
    """
    # Inicializar ProviderManager
    config_path = os.path.join(project_root, config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
        
    manager = ProviderManager(config_path)
    
    # Cambiar proveedor si se solicita
    if provider_name:
        manager.set_provider(provider_name)
    
    # Inicializar agente de base de datos
    db_agent_instance = DBAgent(provider_manager=manager)
    
    # Crear agente CrewAI
    crew_agent = Agent(
        role="Experto en Bases de Datos",
        goal="Consultar y analizar bases de datos de manera eficiente",
        backstory="Soy un experto en bases de datos con amplio conocimiento en SQL y análisis de datos. Mi especialidad es convertir lenguaje natural en consultas SQL precisas y explicar los resultados de forma clara.",
        verbose=True,
        tools=[db_agent_instance.for_crew_ai]
    )
    
    return crew_agent

def run_db_query_with_crew(prompt, connection_params=None, provider_name=None):
    """
    Ejecuta una consulta de base de datos usando CrewAI.
    
    Args:
        prompt: Consulta en lenguaje natural
        connection_params: Parámetros de conexión a la base de datos (opcional)
        provider_name: Nombre del proveedor a utilizar (opcional)
        
    Returns:
        Resultado de la consulta
    """
    # Crear agente
    db_agent = create_db_agent_for_crew(provider_name=provider_name)
    
    # Crear tarea
    task = Task(
        description=prompt,
        expected_output="Consulta SQL, resultados y explicación",
        agent=db_agent,
        kwargs={"connection": connection_params or {"type": "mysql"}}
    )
    
    # Crear crew
    crew = Crew(
        agents=[db_agent],
        tasks=[task],
        verbose=True
    )
    
    # Ejecutar
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    import argparse
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Ejecutar consulta con CrewAI")
    parser.add_argument("--prompt", type=str, required=True, help="Consulta en lenguaje natural")
    parser.add_argument("--type", type=str, default="mysql", help="Tipo de base de datos")
    parser.add_argument("--host", type=str, help="Host de la base de datos")
    parser.add_argument("--port", type=int, help="Puerto de la base de datos")
    parser.add_argument("--user", type=str, help="Usuario de la base de datos")
    parser.add_argument("--password", type=str, help="Contraseña de la base de datos")
    parser.add_argument("--database", type=str, help="Nombre de la base de datos")
    parser.add_argument("--provider", type=str, help="Proveedor de LLM a utilizar")
    
    args = parser.parse_args()
    
    # Preparar parámetros de conexión
    connection = {
        "type": args.type,
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": args.password,
        "database": args.database
    }
    
    # Eliminar valores None
    connection = {k: v for k, v in connection.items() if v is not None}
    
    # Ejecutar consulta
    print(f"🚀 Ejecutando consulta: {args.prompt}")
    result = run_db_query_with_crew(args.prompt, connection, args.provider)
    
    # Mostrar resultado
    print("\n✅ Resultado:")
    print(result)
