#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base abstracta para todos los agentes del sistema.
Define la interfaz común que todos los agentes deben implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from providers.provider_manager import ProviderManager

class BaseAgent(ABC):
    """Clase base abstracta para todos los agentes del sistema."""
    
    def __init__(self, provider_manager: ProviderManager, name: str = "Base Agent"):
        """
        Inicializa el agente con un gestor de proveedores.
        
        Args:
            provider_manager: Gestor de proveedores inicializado
            name: Nombre descriptivo del agente
        """
        self.provider_manager = provider_manager
        self.name = name
        self.description = "Agente base abstracto"
        self.capabilities = []
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Método principal para ejecutar el agente con los datos de entrada.
        
        Args:
            input_data: Datos de entrada para el agente
            **kwargs: Argumentos adicionales específicos del agente
            
        Returns:
            Diccionario con los resultados del agente
        """
        pass
    
    @abstractmethod
    def get_options(self) -> List[Dict[str, Any]]:
        """
        Devuelve las opciones disponibles para este agente.
        
        Returns:
            Lista de diccionarios que describen las opciones disponibles
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Devuelve información sobre el agente.
        
        Returns:
            Diccionario con metadatos del agente
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "provider": self.provider_manager.get_current_provider_name()
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida los datos de entrada para el agente.
        
        Args:
            input_data: Datos a validar
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        # Implementación por defecto, debe ser sobrescrita si se necesita validación específica
        return True