# providers/adapters/crewai_adapter.py
from providers.base_provider import BaseProvider
from typing import Dict, Any, List

class CrewAIAdapter:
    """Adapta los proveedores de t-p para ser compatibles con CrewAI."""
    
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        
    def complete(self, prompt: str) -> str:
        """
        Método compatible con CrewAI que llama al proveedor de t-p.
        
        Args:
            prompt: El prompt a procesar
            
        Returns:
            Texto generado por el proveedor de t-p
        """
        return self.provider.generate_text(prompt)
    
    def name(self) -> str:
        """Devuelve el nombre del modelo adaptado."""
        return f"t-p-{type(self.provider).__name__}"