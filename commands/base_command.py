# En commands/base_command.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCommand(ABC):
    """Clase base para todos los comandos del sistema"""
    
    def __init__(self, name: str = "Base Command"):
        self.name = name
        self.description = "Comando base abstracto"
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el comando con los parámetros especificados.
        
        Args:
            params: Diccionario con parámetros para el comando
            
        Returns:
            Diccionario con los resultados de la ejecución
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Valida si los parámetros son correctos para el comando.
        
        Args:
            params: Diccionario con parámetros a validar
            
        Returns:
            True si los parámetros son válidos, False en caso contrario
        """
        return True