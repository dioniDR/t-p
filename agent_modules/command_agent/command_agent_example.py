#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de uso del CommandAgent con diferentes proveedores de LLM.
Este script demuestra:
- Cómo inicializar el CommandAgent con un ProviderManager
- Cómo procesar diferentes tipos de comandos
- Cómo cambiar entre proveedores
"""

import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importaciones
# Obtenemos la ruta absoluta al directorio raíz del proyecto (dos niveles arriba)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
print(f"Directorio raíz añadido al path: {project_root}")

# Cargar variables de entorno desde .env
load_dotenv()

# Importar los componentes necesarios
from providers.provider_manager import ProviderManager
from agent_modules.command_agent import CommandAgent
from utils.logger import get_logger

# Configurar logger
logger = get_logger("command_agent_example")

def main():
    """Función principal del ejemplo"""
    
    print("🧠 t-p — Ejemplo de CommandAgent")
    print("===============================\n")
    
    # Inicializar el gestor de proveedores
    config_path = os.path.join(project_root, "config", "settings.yaml")
    print(f"Ruta de configuración: {config_path}")
    
    # Verificar que el archivo de configuración existe
    if not os.path.exists(config_path):
        print(f"❌ ERROR: El archivo de configuración no existe en {config_path}")
        print("Directorios disponibles en el proyecto:")
        for item in os.listdir(project_root):
            if os.path.isdir(os.path.join(project_root, item)):
                print(f"- {item}/")
        return
    
    try:
        manager = ProviderManager(config_path=config_path)
        
        # Mostrar proveedores disponibles
        available_providers = manager.list_available_providers()
        print(f"📋 Proveedores disponibles: {', '.join(available_providers)}")
        
        # Obtener el proveedor activo
        current_provider_name = manager.get_current_provider_name()
        print(f"🔍 Proveedor activo: {current_provider_name}\n")
        
        # Inicializar el agente de comandos
        agent = CommandAgent(provider_manager=manager)
        print(f"🤖 Agente inicializado: {agent.name}\n")
        
        # Lista de comandos de ejemplo para probar
        commands = [
            "ayuda",
            "listar proveedores",
            "generar Explica brevemente qué es un modelo de lenguaje",
            "usar claude",
            "resumen La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
            "explicar El aprendizaje por refuerzo es un tipo de machine learning donde un agente aprende a comportarse en un entorno realizando acciones y recibiendo recompensas."
        ]
        
        # Procesar cada comando
        for i, cmd in enumerate(commands, 1):
            print(f"\n🔹 Comando {i}: {cmd}")
            print("🔸 Procesando...")
            
            try:
                result = agent.act(cmd)
                print(f"🔸 Resultado:\n{result}\n")
                print("=" * 50)
            except Exception as e:
                logger.error(f"Error al procesar comando '{cmd}': {e}")
                print(f"❌ Error: {e}")
        
        # Modo interactivo opcional
        interactive = input("\n¿Deseas continuar en modo interactivo? (s/n): ").strip().lower() == 's'
        
        if interactive:
            print("\n🔹 Modo interactivo. Escribe 'salir' para terminar.\n")
            
            while True:
                user_input = input("🧠 > ")
                
                if user_input.lower() in ["salir", "exit", "quit"]:
                    print("👋 ¡Hasta luego!")
                    break
                
                try:
                    result = agent.act(user_input)
                    print(f"\n✅ {result}\n")
                except Exception as e:
                    logger.error(f"Error en modo interactivo: {e}")
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        logger.error(f"Error al inicializar: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Ejemplo interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error general: {e}")
        print(f"\n❌ Error: {e}")