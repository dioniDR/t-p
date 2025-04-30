# core/crew_orchestrator.py
from crewai import Agent, Task, Crew
from providers.provider_manager import ProviderManager
from providers.adapters.crewai_adapter import CrewAIAdapter
from utils.db_system_detector import run as detect_system
from typing import Dict, Any, List
import os
import json

class CrewOrchestrator:
    """Orquestador de agentes crewAI para t-p."""
    
    def __init__(self, provider_manager: ProviderManager):
        """
        Inicializa el orquestador con un gestor de proveedores.
        
        Args:
            provider_manager: Gestor de proveedores de t-p
        """
        self.provider_manager = provider_manager
        self.system_data = None
        self.agents = {}
        
    def detect_system(self) -> Dict[str, Any]:
        """
        Detecta el sistema y guarda los datos para uso por los agentes.
        
        Returns:
            Datos del sistema detectado
        """
        self.system_data = detect_system()
        return self.system_data
    
    def create_database_expert(self) -> Agent:
        """
        Crea un agente experto en bases de datos usando los datos del sistema.
        
        Returns:
            Agente CrewAI experto en bases de datos
        """
        if not self.system_data:
            self.detect_system()
            
        # Obtener datos de bases de datos detectadas
        db_systems = self.system_data.get("database_systems", {})
        
        # Crear un conocimiento especializado basado en los sistemas detectados
        db_knowledge = "Sistemas detectados: "
        if db_systems:
            for db_name, info in db_systems.items():
                db_knowledge += f"{db_name.upper()} (cliente: {'sí' if info['client_available'] else 'no'}, "
                if info["ports_detected"]:
                    db_knowledge += f"puertos: {info['ports_detected']}), "
                else:
                    db_knowledge += "sin puertos detectados), "
        else:
            db_knowledge += "ninguno. "
            
        # Adaptador para el proveedor (preferiblemente Claude por su conocimiento)
        if "claude" in self.provider_manager.providers:
            provider = self.provider_manager.providers["claude"]
        else:
            provider = self.provider_manager.get_provider()
            
        adapter = CrewAIAdapter(provider)
        
        # Crear el agente
        db_expert = Agent(
            name="DatabaseExpert",
            llm=adapter,
            role="Experto en Bases de Datos",
            goal="Analizar y gestionar bases de datos de manera óptima",
            backstory=f"Soy un experto en sistemas de bases de datos con amplia experiencia. {db_knowledge}",
            verbose=True
        )
        
        self.agents["db_expert"] = db_expert
        return db_expert
    
    def create_system_analyst(self) -> Agent:
        """
        Crea un agente analista de sistemas usando los datos del sistema.
        
        Returns:
            Agente CrewAI analista de sistemas
        """
        if not self.system_data:
            self.detect_system()
            
        # Obtener datos del entorno
        env_info = self.system_data.get("environment", {})
        
        # Crear conocimiento especializado
        sys_knowledge = f"Sistema operativo: {env_info.get('system', 'desconocido')} {env_info.get('release', '')}, "
        sys_knowledge += f"Arquitectura: {env_info.get('architecture', 'desconocida')}, "
        sys_knowledge += f"En Docker: {'sí' if env_info.get('in_docker', False) else 'no'}"
        
        # Adaptador para el proveedor (preferiblemente OpenAI por su capacidad técnica)
        if "openai" in self.provider_manager.providers:
            provider = self.provider_manager.providers["openai"]
        else:
            provider = self.provider_manager.get_provider()
            
        adapter = CrewAIAdapter(provider)
        
        # Crear el agente
        system_analyst = Agent(
            name="SystemAnalyst",
            llm=adapter,
            role="Analista de Sistemas",
            goal="Optimizar configuraciones de sistemas y entornos",
            backstory=f"Soy un analista de sistemas experimentado. {sys_knowledge}",
            verbose=True
        )
        
        self.agents["system_analyst"] = system_analyst
        return system_analyst
    
    def create_ollama_agent(self) -> Agent:
        """
        Crea un agente que utiliza Ollama para tareas locales.
        
        Returns:
            Agente CrewAI con Ollama
        """
        # Verificar si tenemos el proveedor de Ollama
        if "ollama" in self.provider_manager.providers:
            provider = self.provider_manager.providers["ollama"]
            adapter = CrewAIAdapter(provider)
            
            # Crear el agente
            ollama_agent = Agent(
                name="LocalAgent",
                llm=adapter,
                role="Asistente Local",
                goal="Procesar tareas localmente sin conexión a internet",
                backstory="Soy un asistente que procesa tareas localmente utilizando modelos de Ollama.",
                verbose=True
            )
            
            self.agents["ollama_agent"] = ollama_agent
            return ollama_agent
        else:
            print("⚠️ Proveedor Ollama no disponible. El agente local no se creará.")
            return None
    
    def create_all_agents(self) -> List[Agent]:
        """
        Crea todos los agentes disponibles.
        
        Returns:
            Lista de agentes creados
        """
        agents = []
        
        # Crear agentes
        db_expert = self.create_database_expert()
        system_analyst = self.create_system_analyst()
        ollama_agent = self.create_ollama_agent()
        
        # Agregar agentes a la lista
        if db_expert:
            agents.append(db_expert)
        if system_analyst:
            agents.append(system_analyst)
        if ollama_agent:
            agents.append(ollama_agent)
            
        return agents
    
    def run_database_analysis(self, prompt: str = None) -> str:
        """
        Ejecuta un análisis de bases de datos con CrewAI.
        
        Args:
            prompt: Instrucción específica (opcional)
            
        Returns:
            Resultado del análisis
        """
        if not self.system_data:
            self.detect_system()
        
        if not prompt:
            prompt = "Analiza las bases de datos detectadas y proporciona recomendaciones."
            
        # Crear agentes si no existen
        if "db_expert" not in self.agents:
            self.create_database_expert()
        if "system_analyst" not in self.agents:
            self.create_system_analyst()
            
        # Crear tareas
        tasks = [
            Task(
                description=f"Analiza los siguientes sistemas de bases de datos y proporciona recomendaciones:\n{json.dumps(self.system_data.get('database_systems', {}), indent=2)}",
                agent=self.agents["db_expert"],
                expected_output="Análisis detallado de los sistemas de bases de datos detectados con recomendaciones"
            ),
            Task(
                description="Basado en el análisis anterior, proporciona configuraciones óptimas para el entorno detectado.",
                agent=self.agents["system_analyst"],
                expected_output="Configuraciones recomendadas para el sistema actual"
            )
        ]
        
        # Crear y ejecutar el crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result