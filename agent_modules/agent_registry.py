#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Registro central de agentes disponibles en el sistema.
Permite descubrir y cargar agentes dinámicamente.
"""

import os
import importlib
import inspect
from typing import Dict, Type, List, Optional

from .base_agent import BaseAgent

class AgentRegistry:
    """Registro de todos los agentes disponibles en el sistema."""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, agent_id: str, agent_class: Type[BaseAgent]):
        """
        Registra un agente en el sistema.
        
        Args:
            agent_id: Identificador único del agente
            agent_class: Clase que implementa el agente
        """
        if not inspect.isclass(agent_class) or not issubclass(agent_class, BaseAgent):
            raise TypeError(f"El agente debe ser una subclase de BaseAgent: {agent_class}")
        
        cls._agents[agent_id] = agent_class
    
    @classmethod
    def get_agent_class(cls, agent_id: str) -> Optional[Type[BaseAgent]]:
        """
        Obtiene la clase de agente por su ID.
        
        Args:
            agent_id: Identificador del agente
            
        Returns:
            Clase del agente o None si no existe
        """
        return cls._agents.get(agent_id)
    
    @classmethod
    def get_all_agents(cls) -> Dict[str, Type[BaseAgent]]:
        """
        Devuelve todos los agentes registrados.
        
        Returns:
            Diccionario de agentes registrados (id: clase)
        """
        return cls._agents.copy()
    
    @classmethod
    def list_agents(cls) -> List[Dict[str, str]]:
        """
        Lista todos los agentes disponibles con su información básica.
        
        Returns:
            Lista de diccionarios con información de los agentes
        """
        result = []
        for agent_id, agent_class in cls._agents.items():
            # Crear una instancia temporal para obtener información
            temp_instance = agent_class.__new__(agent_class)
            temp_instance.name = getattr(agent_class, 'name', agent_id)
            temp_instance.description = getattr(agent_class, 'description', 'Sin descripción')
            
            result.append({
                "id": agent_id,
                "name": temp_instance.name,
                "description": temp_instance.description
            })
        
        return result
    
    @classmethod
    def discover_agents(cls):
        """
        Descubre y registra automáticamente los agentes disponibles.
        Escanea el directorio 'agent_modules' en busca de módulos agent.py.
        """
        # Obtener el directorio base de los módulos de agentes
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Escanear subdirectorios en busca de agentes
        for item in os.listdir(current_dir):
            # Ignorar archivos y directorios que comienzan con _
            if item.startswith('_') or not os.path.isdir(os.path.join(current_dir, item)):
                continue
            
            # Verificar si existe agent.py
            agent_module_path = os.path.join(current_dir, item, 'agent.py')
            if not os.path.exists(agent_module_path):
                continue
            
            try:
                # Importar el módulo
                module_name = f"agent_modules.{item}.agent"
                module = importlib.import_module(module_name)
                
                # Buscar clases que hereden de BaseAgent
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseAgent) and obj != BaseAgent:
                        # Registrar el agente
                        agent_id = item  # Usar el nombre del directorio como ID
                        cls.register(agent_id, obj)
                        break
            except (ImportError, AttributeError) as e:
                print(f"Error al cargar el agente {item}: {e}")