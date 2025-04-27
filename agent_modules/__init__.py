"""
Módulo de agentes para t-p.
Proporciona una estructura modular para integrar diferentes agentes
que aprovechan los proveedores de modelos de lenguaje.
"""

from .base_agent import BaseAgent
from .agent_registry import AgentRegistry

# Inicialización automática del registro de agentes
AgentRegistry.discover_agents()

__version__ = '0.1.0'