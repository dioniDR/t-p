# Versión simplificada de test_crew_integration.py
import os
import sys
from providers.provider_manager import ProviderManager
from utils.db_system_detector import run as detect_system
from crewai import Agent, Task, Crew

# Crear adaptador para el proveedor
class CrewAIAdapter:
    """Adaptador simple para hacer compatibles los proveedores de t-p con CrewAI."""
    
    def __init__(self, provider):
        self.provider = provider
    
    def complete(self, prompt, **kwargs):
        """Método requerido por CrewAI."""
        return self.provider.generate_text(prompt)
    
    def name(self):
        """Devuelve el nombre del modelo."""
        return f"t-p-{type(self.provider).__name__}"

# Cargar la configuración
config_path = os.path.join("config", "settings.yaml")
manager = ProviderManager(config_path)

# Detectar el sistema
print("🔍 Detectando el sistema...")
system_data = detect_system()
print("✅ Sistema detectado")

# Usar el proveedor actual
provider = manager.get_provider()
print(f"🔌 Usando proveedor: {manager.get_current_provider_name()}")

# Adaptar el proveedor para CrewAI
adapted_provider = CrewAIAdapter(provider)

try:
    # Crear el agente simple manera directa
    print("🧠 Creando agente...")
    agent = Agent(
        role="Analista de Sistemas",
        goal="Analizar sistemas y bases de datos",
        backstory="Experto en análisis de sistemas informáticos y bases de datos.",
        verbose=True,
        llm=adapted_provider
    )
    print("✅ Agente creado exitosamente")
    
    # Crear una tarea simple
    print("📝 Creando tarea...")
    task = Task(
        description=f"Analiza este sistema: {system_data['environment']['system']}",
        expected_output="Un análisis detallado del sistema.",
        agent=agent
    )
    print("✅ Tarea creada exitosamente")
    
    # OPCIONAL: Descomentar para ejecutar realmente
    # print("🚀 Iniciando análisis...")
    # crew = Crew(
    #     agents=[agent],
    #     tasks=[task],
    #     verbose=True
    # )
    # result = crew.kickoff()
    # print(f"✅ Análisis completado")
    
    print("⚠️ Ejecución real comentada para evitar llamadas API en esta prueba")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print(traceback.format_exc())

print("\n✅ Prueba de integración básica finalizada")
