import os
import argparse
from dotenv import load_dotenv
from providers.provider_manager import ProviderManager

def main():
    # Cargar variables de entorno
    load_dotenv()

    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Proveedor Inteligente de Lenguaje")
    
    # Argumentos principales
    parser.add_argument('--provider', 
                        choices=['openai', 'claude'], 
                        default=None, 
                        help="Seleccionar proveedor específico")
    parser.add_argument('--prompt', 
                        type=str, 
                        help="Prompt para generar texto")
    parser.add_argument('--max-tokens', 
                        type=int, 
                        default=300, 
                        help="Número máximo de tokens (default: 300)")
    parser.add_argument('--temperature', 
                        type=float, 
                        default=0.7, 
                        help="Temperatura de generación (default: 0.7)")
    
    # Modos de operación
    parser.add_argument('--list-providers', 
                        action='store_true', 
                        help="Listar proveedores disponibles")
    parser.add_argument('--info', 
                        action='store_true', 
                        help="Mostrar información del sistema")

    # Parsear argumentos
    args = parser.parse_args()

    # Comando de ayuda
    if '--help' in args:
        parser.print_help()
        return

    # Ruta al archivo de configuración
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.yaml')

    try:
        # Crear el gestor de proveedores
        manager = ProviderManager(config_path)

        # Modo de listar proveedores
        if args.list_providers:
            print("🌐 Proveedores disponibles:")
            for provider in manager.list_available_providers():
                print(f"- {provider}")
            return

        # Modo de información del sistema
        if args.info:
            print("🤖 Información del Sistema de Proveedores de Lenguaje")
            print(f"Proveedor por defecto: {manager.get_current_provider_name()}")
            print("Proveedores disponibles:", manager.list_available_providers())
            return

        # Selección de proveedor
        if args.provider:
            manager.set_provider(args.provider)

        # Generación de texto
        if args.prompt:
            print("🚀 Generando texto:")
            respuesta = manager.get_provider().generate_text(
                args.prompt, 
                max_tokens=args.max_tokens, 
                temperature=args.temperature
            )
            print("\n📝 Respuesta:\n", respuesta)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
