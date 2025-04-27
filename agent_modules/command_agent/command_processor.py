#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de comandos para t-p.
Interpreta comandos del usuario y los dirige al proveedor de LLM adecuado.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple

class CommandProcessor:
    """
    Procesa comandos de texto y los dirige al proveedor de LLM correspondiente.
    Proporciona una interfaz para interpretar comandos simples o complejos.
    """
    
    def __init__(self, provider_manager=None):
        """
        Inicializa el procesador de comandos.
        
        Args:
            provider_manager: Gestor de proveedores (opcional)
        """
        self.provider_manager = provider_manager
        self.command_patterns = {
            r"(?i)^usar\s+(\w+)": self._use_provider,
            r"(?i)^generar\s+(.+)": self._generate_text,
            r"(?i)^listar\s+(\w+)": self._list_items,
            r"(?i)^ayuda": self._show_help,
        }
        
        # Comandos de utilidad comunes
        self.utility_commands = {
            "resumen": self._summarize_text,
            "analizar": self._analyze_text,
            "traducir": self._translate_text,
            "corregir": self._correct_text,
            "explicar": self._explain_text,
        }
    
    def process(self, command_text: str) -> str:
        """
        Procesa un comando de texto y devuelve el resultado.
        
        Args:
            command_text: Texto del comando a procesar
            
        Returns:
            Resultado del procesamiento del comando
        """
        if not command_text or command_text.strip() == "":
            return "Por favor ingresa un comando. Escribe 'ayuda' para ver los comandos disponibles."
        
        # Verificar si el comando coincide con algún patrón
        for pattern, handler in self.command_patterns.items():
            match = re.search(pattern, command_text)
            if match:
                return handler(match.group(1) if len(match.groups()) > 0 else "")
        
        # Buscar comandos de utilidad
        command_parts = command_text.strip().split(" ", 1)
        command = command_parts[0].lower()
        
        if command in self.utility_commands and len(command_parts) > 1:
            return self.utility_commands[command](command_parts[1])
        
        # Si no es un comando reconocido, procesarlo como texto para el LLM
        return self._process_with_llm(command_text)
    
    def _use_provider(self, provider_name: str) -> str:
        """Cambia al proveedor especificado."""
        if not self.provider_manager:
            return "No hay un gestor de proveedores disponible."
        
        try:
            self.provider_manager.set_provider(provider_name.lower())
            return f"Proveedor cambiado a: {provider_name}"
        except ValueError as e:
            available = ", ".join(self.provider_manager.list_available_providers())
            return f"Error: {str(e)}. Proveedores disponibles: {available}"
    
    def _generate_text(self, prompt: str) -> str:
        """Genera texto usando el proveedor actual."""
        if not self.provider_manager:
            return "No hay un gestor de proveedores disponible."
        
        try:
            return self.provider_manager.get_provider().generate_text(prompt)
        except Exception as e:
            return f"Error al generar texto: {str(e)}"
    
    def _list_items(self, item_type: str) -> str:
        """Lista elementos del sistema según el tipo."""
        if not self.provider_manager:
            return "No hay un gestor de proveedores disponible."
        
        if item_type.lower() == "proveedores":
            providers = self.provider_manager.list_available_providers()
            current = self.provider_manager.get_current_provider_name()
            result = "Proveedores disponibles:\n"
            for p in providers:
                result += f"- {p}" + (" (activo)" if p == current else "") + "\n"
            return result
        
        return f"No se reconoce el tipo de elemento '{item_type}'"
    
    def _show_help(self, _=None) -> str:
        """Muestra la ayuda de comandos disponibles."""
        return """
Comandos disponibles:
- usar <proveedor>: Cambia al proveedor especificado (openai, claude, etc.)
- generar <texto>: Genera texto con el prompt especificado
- listar proveedores: Muestra los proveedores disponibles
- resumen <texto>: Resume el texto proporcionado
- analizar <texto>: Analiza el texto proporcionado
- traducir <texto>: Traduce el texto proporcionado
- corregir <texto>: Corrige errores en el texto
- explicar <texto>: Explica el texto proporcionado
- ayuda: Muestra esta ayuda
        """
    
    def _process_with_llm(self, text: str) -> str:
        """Procesa el texto usando el LLM actual."""
        if not self.provider_manager:
            return f"No hay un gestor de proveedores. Texto recibido: {text}"
        
        try:
            return self.provider_manager.get_provider().generate_text(text)
        except Exception as e:
            return f"Error al procesar con LLM: {str(e)}"
    
    # Comandos de utilidad
    
    def _summarize_text(self, text: str) -> str:
        """Resume el texto proporcionado."""
        prompt = f"Resume el siguiente texto de manera concisa:\n\n{text}"
        return self._process_with_llm(prompt)
    
    def _analyze_text(self, text: str) -> str:
        """Analiza el texto proporcionado."""
        prompt = f"Analiza el siguiente texto, destacando puntos clave, tono, y estructura:\n\n{text}"
        return self._process_with_llm(prompt)
    
    def _translate_text(self, text: str) -> str:
        """Traduce el texto proporcionado."""
        # Detectar idioma objetivo
        target_lang = "español"  # Idioma por defecto
        lang_pattern = r"(?i)a\s+(\w+):\s*(.+)"
        match = re.search(lang_pattern, text)
        
        if match:
            target_lang = match.group(1)
            text = match.group(2)
        
        prompt = f"Traduce el siguiente texto al {target_lang}:\n\n{text}"
        return self._process_with_llm(prompt)
    
    def _correct_text(self, text: str) -> str:
        """Corrige errores en el texto."""
        prompt = f"Corrige los errores gramaticales y ortográficos en el siguiente texto:\n\n{text}"
        return self._process_with_llm(prompt)
    
    def _explain_text(self, text: str) -> str:
        """Explica el texto proporcionado."""
        prompt = f"Explica el siguiente texto de manera clara y sencilla:\n\n{text}"
        return self._process_with_llm(prompt)