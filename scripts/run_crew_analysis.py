# scripts/run_crew_analysis.py
import os
import sys
import argparse
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Cargar variables de entorno
load_dotenv()

from providers.provider_manager import ProviderManager
from core.crew_orchestrator import CrewOrchestrator

def main():
    # Crear parser de argumentos
    parser = argparse.ArgumentParser(description="Análisis de sistema con CrewAI")
    parser.add_argument("--detect-only", action="store_true", help="Solo detectar el sistema sin análisis")
    parser.add_argument("--prompt", type=str, help="Instrucción específica para el análisis")
    parser.add_argument("--output", type=str, help="Archivo para guardar el resultado")
    parser.add_argument("--config", type=str, default="config/settings.yaml", help="Ruta al archivo de configuración")
    
    args = parser.parse_args()
    
    try:
        print("🚀 Iniciando orquestador de CrewAI para t-p...")
        
        # Inicializar el gestor de proveedores
        config_path = os.path.abspath(args.config)
        manager = ProviderManager(config_path)
        
        # Crear y configurar el orquestador
        orchestrator = CrewOrchestrator(manager)
        
        # Detectar el sistema
        print("🔍 Detectando el sistema...")
        system_data = orchestrator.detect_system()
        
        print("✅ Sistema detectado:")
        print(f"  - Sistema: {system_data['environment']['system']} {system_data['environment']['release']}")
        print(f"  - Arquitectura: {system_data['environment']['architecture']}")
        
        # Si solo se solicita detección, terminar aquí
        if args.detect_only:
            print("⚙️ Solo se solicitó detección del sistema. Finalizando.")
            return
        
        # Ejecutar análisis
        print("\n🧠 Ejecutando análisis de CrewAI...")
        result = orchestrator.run_database_analysis(args.prompt)
        
        # Mostrar resultado
        print("\n📊 Resultado del análisis:")
        print(result)
        
        # Guardar resultado si se solicita
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n💾 Resultado guardado en: {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())