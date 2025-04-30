# scripts/db_analysis_crew.py (versión corregida)

import os
import sys
import argparse
import json
from datetime import datetime

# Añadir el directorio raíz al path si es necesario
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from providers.provider_manager import ProviderManager
from utils.db_system_detector import run as detect_system
from crewai import Agent, Task, Crew

def create_output_dir(base_dir="./output"):
    """Crea un directorio para guardar los resultados."""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Crear un subdirectorio con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, f"analysis_{timestamp}")
    os.makedirs(output_dir)
    
    return output_dir

def main():
    # Configurar argumentos
    parser = argparse.ArgumentParser(description="Análisis de bases de datos con CrewAI")
    parser.add_argument("--detect-only", action="store_true", help="Solo detectar el sistema")
    parser.add_argument("--provider", type=str, help="Nombre del proveedor a utilizar")
    parser.add_argument("--config", type=str, default="config/settings.yaml", 
                      help="Ruta del archivo de configuración")
    parser.add_argument("--save", action="store_true", help="Guardar resultados en archivos")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo", 
                      help="Modelo de OpenAI a utilizar (default: gpt-3.5-turbo)")
    args = parser.parse_args()
    
    try:
        print("🚀 Iniciando análisis de bases de datos con CrewAI...")
        
        # Cargar configuración
        config_path = os.path.abspath(args.config)
        if not os.path.exists(config_path):
            print(f"❌ Archivo de configuración no encontrado: {config_path}")
            return 1
        
        manager = ProviderManager(config_path)
        
        # Seleccionar proveedor
        if args.provider:
            try:
                manager.set_provider(args.provider)
                print(f"✅ Proveedor cambiado a: {args.provider}")
            except ValueError as e:
                print(f"❌ Error al seleccionar proveedor: {e}")
                available = manager.list_available_providers()
                print(f"📋 Proveedores disponibles: {', '.join(available)}")
                return 1
        
        provider_name = manager.get_current_provider_name()
        print(f"🔌 Usando proveedor: {provider_name}")
        
        # Detectar sistema
        print("\n🔍 Detectando el sistema...")
        system_data = detect_system()
        
        # Mostrar resumen básico del sistema
        print("\n📊 Resumen del sistema:")
        print(f"  Sistema: {system_data['environment']['system']} {system_data['environment']['release']}")
        print(f"  Arquitectura: {system_data['environment']['architecture']}")
        
        db_systems = system_data.get('database_systems', {})
        if db_systems:
            print(f"  Bases de datos detectadas: {', '.join(db_systems.keys())}")
        else:
            print("  No se detectaron bases de datos disponibles")
        
        # Si solo se solicita detección, terminar aquí
        if args.detect_only:
            print("\n✅ Detección completada")
            
            if args.save:
                output_dir = create_output_dir()
                system_file = os.path.join(output_dir, "system_data.json")
                with open(system_file, 'w', encoding='utf-8') as f:
                    json.dump(system_data, f, indent=2)
                print(f"💾 Datos del sistema guardados en: {system_file}")
            
            return 0
        
        # Crear agentes
        print("\n🧠 Creando agentes...")
        
        # Usar el modelo especificado o el predeterminado
        model = args.model
        
        db_expert = Agent(
            role="Experto en Bases de Datos",
            goal="Analizar sistemas de bases de datos y proporcionar recomendaciones de optimización",
            backstory="Consultor senior con décadas de experiencia en administración y optimización de bases de datos.",
            verbose=True,
            allow_delegation=False,
            llm_config={"model": model}
        )
        
        system_analyst = Agent(
            role="Analista de Sistemas",
            goal="Evaluar la configuración del sistema y sugerir mejoras",
            backstory="Especialista en análisis de sistemas operativos y configuraciones de hardware.",
            verbose=True,
            allow_delegation=False,
            llm_config={"model": model}
        )
        
        print("✅ Agentes creados exitosamente")
        
        # Crear tareas
        print("\n📝 Creando tareas...")
        
        # Convertir datos del sistema a formato texto para las tareas
        system_env = json.dumps(system_data['environment'], indent=2)
        system_db = json.dumps(system_data.get('database_systems', {}), indent=2)
        
        db_analysis_task = Task(
            description=f"Analiza las siguientes bases de datos detectadas y proporciona recomendaciones:\n\n{system_db}",
            expected_output="Análisis detallado de los sistemas de bases de datos con recomendaciones de optimización",
            agent=db_expert
        )
        
        system_analysis_task = Task(
            description=f"Analiza el siguiente entorno y proporciona recomendaciones de configuración:\n\n{system_env}",
            expected_output="Análisis del entorno con recomendaciones para optimizar el rendimiento",
            agent=system_analyst
        )
        
        print("✅ Tareas creadas exitosamente")
        
        # Ejecutar el análisis
        print("\n🚀 Iniciando análisis con CrewAI...")
        
        crew = Crew(
            agents=[db_expert, system_analyst],
            tasks=[db_analysis_task, system_analysis_task],
            verbose=True
        )
        
        # Ejecutar y obtener resultado
        result = crew.kickoff()
        
        # Convertir el resultado a string si es necesario
        result_text = str(result)
        
        print("\n✅ Análisis completado")
        print("\n📊 Resultado del análisis:")
        print(result_text)
        
        # Guardar resultados si se solicita
        if args.save:
            output_dir = create_output_dir()
            
            # Guardar datos del sistema
            system_file = os.path.join(output_dir, "system_data.json")
            with open(system_file, 'w', encoding='utf-8') as f:
                json.dump(system_data, f, indent=2)
                
            # Guardar resultado del análisis como string
            result_file = os.path.join(output_dir, "analysis_result.txt")
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(result_text)  # Usar la versión string del resultado
                
            print(f"\n💾 Resultados guardados en: {output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())