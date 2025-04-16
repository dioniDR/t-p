import os
import yaml
from providers.openai_provider import OpenAIProvider
from providers.claude_provider import ClaudeProvider

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
            if name == "openai":
                self.providers[name] = OpenAIProvider(**cfg)
            elif name == "claude":
                self.providers[name] = ClaudeProvider(**cfg)

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
