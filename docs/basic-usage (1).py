#!/usr/bin/env python3
"""
Ejemplo básico de uso del sistema t-p con diferentes proveedores de LLM.
Este script demuestra:
- Cómo inicializar el gestor de proveedores
- Cómo generar texto con el proveedor activo
- Cómo cambiar de proveedor en tiempo de ejecución
"""

import os
import sys
import time
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cargar variables de entorno desde .env
load_dotenv()

# Importar el gestor de proveedores
from providers.provider_manager import ProviderManager
from utils.logger import get_logger

# Configurar logger
logger = get_logger("basic_usage")

def main():
    """Función principal del ejemplo"""
    
    print("🧠 t-p — Proveedor Inteligente de Lenguaje")
    print("==========================================\n")
    
    # Inicializar el gestor de proveedores
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    manager = ProviderManager(config_path=config_path)
    
    # Mostrar proveedores disponibles
    available_providers = manager.list_available_providers()
    print(f"📋 Proveedores disponibles: {', '.join(available_providers)}")
    
    # Obtener el proveedor activo
    current_provider_name = manager.get_current_provider_name()
    print(f"🔍 Proveedor activo: {current_provider_name}\n")
    
    # Ejemplo 1: Generar texto con el proveedor por defecto
    prompt1 = "Explica brevemente qué son los modelos de lenguaje"
    
    print(f"🤔 Prompt: {prompt1}")
    print("⏳ Generando respuesta...")
    
    start_time = time.time()
    response1 = manager.get_provider().generate_text(prompt1)
    elapsed_time = time.time() - start_time
    
    print(f"⏱️ Tiempo: {elapsed_time:.2f} segundos")
    print(f"💬 Respuesta:\n{response1}\n")
    
    # Ejemplo 2: Cambiar a otro proveedor
    if len(available_providers) > 1:
        # Seleccionar un proveedor diferente al actual
        next_provider = [p for p in available_providers if p != current_provider_name][0]
        
        print(f"🔄 Cambiando a proveedor: {next_provider}")
        manager.set_provider(next_provider)
        
        # Generar texto con el nuevo proveedor
        prompt2 = "¿Cuáles son las ventajas de la arquitectura modular en software?"
        
        print(f"🤔 Prompt: {prompt2}")
        print("⏳ Generando respuesta...")
        
        start_time = time.time()
        response2 = manager.get_provider().generate_text(prompt2)
        elapsed_time = time.time() - start_time
        
        print(f"⏱️ Tiempo: {elapsed_time:.2f} segundos")
        print(f"💬 Respuesta:\n{response2}\n")
    
    # Ejemplo 3: Usar método alternativo para consulta puntual
    prompt3 = "Resume en tres líneas qué es la inferencia en modelos de IA"
    other_provider = available_providers[0]
    
    print(f"📝 Consultando directamente a '{other_provider}' sin cambiar el proveedor activo")
    print(f"🤔 Prompt: {prompt3}")
    print("⏳ Generando respuesta...")
    
    start_time = time.time()
    response3 = manager.ask_provider(other_provider, prompt3)
    elapsed_time = time.time() - start_time
    
    print(f"⏱️ Tiempo: {elapsed_time:.2f} segundos")
    print(f"💬 Respuesta:\n{response3}\n")
    
    print("✅ Ejemplo completado")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Ejemplo interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
