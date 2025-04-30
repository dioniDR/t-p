# En providers/provider_manager.py
import os
import yaml
from providers.llm.openai_provider import OpenAIProvider
from providers.llm.claude_provider import ClaudeProvider
from providers.llm.ollama_provider import OllamaProvider


class ProviderManager:
    def __init__(self, config_path):
        print("✔️ ProviderManager importado correctamente")
        with open(config_path, 'r') as f:
            raw_config = f.read()

        # Expande ${VAR} con los valores del entorno
        expanded = os.path.expandvars(raw_config)
        config = yaml.safe_load(expanded)

        self.providers = {}
        self.current_provider = None

        for name, cfg in config.get("providers", {}).items():
            # Eliminar keys que no son reconocidas por el constructor
            provider_config = {k: v for k, v in cfg.items() if k in ['api_key', 'base_url', 'default_model']}
            
            if name == "openai":
                self.providers[name] = OpenAIProvider(**provider_config)
            elif name == "claude":
                self.providers[name] = ClaudeProvider(**provider_config)
            elif name == "ollama":
                self.providers[name] = OllamaProvider(**provider_config)

        provider_name = config.get("default_provider", "openai")
        if provider_name in self.providers:
            self.current_provider = self.providers[provider_name]
        else:
            raise ValueError(f"Proveedor por defecto no soportado: {provider_name}")

    def get_provider(self):
        return self.current_provider

    def set_provider(self, name):
        if name not in self.providers:
            raise ValueError(f"Proveedor '{name}' no disponible. Usa uno de: {list(self.providers.keys())}")
        self.current_provider = self.providers[name]
        print(f"🔄 Proveedor cambiado a: {name}")

    def list_available_providers(self):
        return list(self.providers.keys())

    def get_current_provider_name(self):
        return type(self.current_provider).__name__ if self.current_provider else "None"

    def ask_provider(self, provider_name, prompt):
        """Consulta a un proveedor específico sin cambiar el proveedor actual"""
        if provider_name not in self.providers:
            raise ValueError(f"Proveedor '{provider_name}' no disponible")
        return self.providers[provider_name].generate_text(prompt)

    # Añadir a providers/provider_manager.py

    def get_crew_adapter(self, provider_name=None):
        """
        Obtiene un adaptador CrewAI para el proveedor especificado.
        
        Args:
            provider_name: Nombre del proveedor a adaptar (optional)
            
        Returns:
            Adaptador CrewAI para el proveedor
        """
        from providers.adapters.crewai_adapter import CrewAIAdapter
        
        if provider_name:
            if provider_name not in self.providers:
                raise ValueError(f"Proveedor '{provider_name}' no disponible")
            provider = self.providers[provider_name]
        else:
            provider = self.get_provider()
            
        return CrewAIAdapter(provider)