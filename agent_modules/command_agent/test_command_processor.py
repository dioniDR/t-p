#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar directamente el CommandProcessor.
Permite enviar instrucciones directamente al procesador sin pasar por el CommandAgent.

Uso:
python test_command_processor.py "comando a ejecutar"
python test_command_processor.py  # Modo interactivo si no se pasan argumentos
"""

import os
import sys
import argparse

# Añadir el directorio raíz al path para importaciones
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Importar componentes necesarios
from providers.provider_manager import ProviderManager
from agent_modules.command_agent.command_processor import CommandProcessor

def main():
    """Función principal"""
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Prueba de CommandProcessor')
    parser.add_argument('command', nargs='?', default=None, 
                      help='Comando a procesar. Si no se proporciona, se inicia el modo interactivo.')
    args = parser.parse_args()
    
    # Inicializar el gestor de proveedores
    config_path = os.path.join(project_root, "config", "settings.yaml")
    
    # Verificar que existe el archivo de configuración
    if not os.path.exists(config_path):
        print(f"❌ ERROR: El archivo de configuración no existe en {config_path}")
        return
    
    try:
        print("🔄 Inicializando ProviderManager...")
        manager = ProviderManager(config_path=config_path)
        
        print("📋 Proveedores disponibles:", ', '.join(manager.list_available_providers()))
        print("🔍 Proveedor activo:", manager.get_current_provider_name())
        
        # Inicializar el procesador de comandos
        print("🧠 Inicializando CommandProcessor...\n")
        processor = CommandProcessor(provider_manager=manager)
        
        # Modo de ejecución
        if args.command:
            # Ejecutar un solo comando pasado como argumento
            result = processor.process(args.command)
            print(f"\n✅ Resultado:\n{result}")
        else:
            # Modo interactivo
            print("🔹 Modo interactivo. Escribe 'salir' para terminar.")
            print("🔹 Comandos disponibles: ayuda, usar, generar, listar, resumen, analizar, traducir, corregir, explicar")
            
            while True:
                user_input = input("\n🧠 > ")
                
                if user_input.lower() in ["salir", "exit", "quit", "q"]:
                    print("👋 ¡Hasta luego!")
                    break
                
                try:
                    result = processor.process(user_input)
                    print(f"\n✅ Resultado:\n{result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error al inicializar: {e}")

if __name__ == "__main__":
    main()