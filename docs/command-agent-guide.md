# Guía de Uso: CommandAgent

## Descripción

El `CommandAgent` es un sistema modular diseñado para interpretar comandos de texto y ejecutar tareas utilizando diferentes proveedores de LLM (Modelos de Lenguaje). Permite cambiar fácilmente entre proveedores como OpenAI, Claude o modelos locales con Ollama.

## Estructura

El `CommandAgent` está compuesto por varios módulos:

- **Agent**: Coordinador principal que recibe y procesa las entradas
- **CommandProcessor**: Interpreta comandos especiales y los dirige al proveedor adecuado
- **TaskGenerator**: Genera tareas basadas en texto de entrada
- **TaskExecutor**: Ejecuta las tareas generadas

## Instalación

1. Asegúrate de tener los archivos necesarios en la estructura correcta:

```
agent_modules/
└── command_agent/
    ├── __init__.py
    ├── agent.py
    ├── command_processor.py
    ├── task_generator.py
    └── task_executor.py
```

2. Configura tus claves API en el archivo `.env`:

```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Uso Básico

```python
from providers.provider_manager import ProviderManager
from agent_modules.command_agent import CommandAgent

# Inicializar el gestor de proveedores
manager = ProviderManager("path/to/config/settings.yaml")

# Crear el agente de comandos
agent = CommandAgent(provider_manager=manager)

# Procesar un comando
result = agent.act("generar Una historia corta sobre robots")
print(result)

# Cambiar de proveedor
result = agent.act("usar claude")
print(result)

# Solicitar ayuda
result = agent.act("ayuda")
print(result)
```

## Comandos Disponibles

### Comandos de Sistema

- `usar <proveedor>`: Cambia al proveedor especificado (openai, claude, etc.)
- `listar proveedores`: Muestra los proveedores disponibles
- `ayuda`: Muestra la ayuda de comandos disponibles

### Comandos de Generación

- `generar <texto>`: Genera texto con el prompt especificado

### Comandos de Utilidad

- `resumen <texto>`: Resume el texto proporcionado
- `analizar <texto>`: Analiza el texto proporcionado
- `traducir <texto>`: Traduce el texto proporcionado
- `traducir a inglés: <texto>`: Traduce a un idioma específico
- `corregir <texto>`: Corrige errores en el texto
- `explicar <texto>`: Explica el texto proporcionado

## Ejemplo en Jupyter Notebook

```python
import os
import sys
from pathlib import Path

# Configurar path del proyecto
project_root = Path().resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importar componentes
from providers.provider_manager import ProviderManager
from agent_modules.command_agent import CommandAgent

# Inicializar
config_path = "config/settings.yaml"
manager = ProviderManager(config_path)
agent = CommandAgent(provider_manager=manager)

# Procesar comandos
commands = [
    "listar proveedores",
    "generar Un poema sobre la tecnología",
    "usar claude",
    "resumen La inteligencia artificial ha avanzado mucho en los últimos años."
]

for cmd in commands:
    print(f"Comando: {cmd}")
    print(f"Resultado: {agent.act(cmd)}")
    print("---")
```

## Personalización

Puedes extender las capacidades del `CommandAgent` modificando estos archivos:

- `command_processor.py`: Para añadir nuevos comandos o modificar los existentes
- `task_generator.py`: Para personalizar cómo se generan las tareas
- `task_executor.py`: Para cambiar la forma en que se ejecutan las tareas

## Resolución de Problemas

- Si encuentras errores de importación, verifica la estructura de directorios y las rutas
- Si hay errores de API, asegúrate de que las claves API están correctamente configuradas
- Para problemas con el modelo local (Ollama), verifica que el servidor local está funcionando
