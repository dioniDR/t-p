# Editar archivo: agent_modules/db_agent/query_builder.py
from typing import Dict, Any, Optional
from providers.provider_manager import ProviderManager

class QueryBuilder:
    """
    Construye consultas SQL basadas en lenguaje natural.
    Utiliza un LLM para generar SQL basado en la estructura de la base de datos.
    """
    
    def __init__(self, provider_manager: ProviderManager):
        """
        Inicializa el constructor de consultas.
        
        Args:
            provider_manager: Gestor de proveedores de LLM
        """
        self.provider_manager = provider_manager
    
    def build_query(self, natural_query: str, db_connection: Dict[str, Any], db_mapping: Optional[Dict] = None) -> str:
        """
        Construye una consulta SQL a partir de lenguaje natural.
        
        Args:
            natural_query: Consulta en lenguaje natural
            db_connection: Información de conexión a la base de datos
            db_mapping: Mapeo de la estructura de la base de datos (opcional)
            
        Returns:
            Consulta SQL generada
        """
        # Obtener el proveedor de LLM
        provider = self.provider_manager.get_provider()
        
        # Construir prompt para el LLM
        prompt = self._build_sql_generation_prompt(natural_query, db_connection, db_mapping)
        
        # Generar SQL usando el LLM
        response = provider.generate_text(prompt)
        
        # Extraer SQL de la respuesta
        sql_query = self._extract_sql_from_response(response)
        
        return sql_query
    
    def _build_sql_generation_prompt(self, natural_query: str, db_connection: Dict[str, Any], db_mapping: Optional[Dict] = None) -> str:
        """
        Construye un prompt para generar SQL.
        
        Args:
            natural_query: Consulta en lenguaje natural
            db_connection: Información de conexión a la base de datos
            db_mapping: Mapeo de la estructura de la base de datos (opcional)
            
        Returns:
            Prompt para el LLM
        """
        db_type = db_connection.get('type', 'mysql').lower()
        db_name = db_connection.get('database', '')
        
        # Base del prompt
        prompt = f"""Como experto en bases de datos {db_type.upper()}, genera una consulta SQL para la siguiente solicitud:

Solicitud: {natural_query}

Base de datos: {db_name}
"""
        
        # Añadir información de estructura si está disponible
        if db_mapping and 'tables' in db_mapping:
            prompt += "\nEstructura de la base de datos:\n"
            
            for table_name, table_info in db_mapping['tables'].items():
                prompt += f"\nTabla: {table_name}\n"
                prompt += f"Columnas: {', '.join(table_info.get('columns', []))}\n"
        
        # Instrucciones finales
        prompt += """
Genera ÚNICAMENTE código SQL válido para esta consulta.
Solo devuelve la consulta SQL, sin explicaciones adicionales.
Usa la sintaxis apropiada para {db_type}.
"""
        
        return prompt
    
    def _extract_sql_from_response(self, response: str) -> str:
        """
        Extrae la consulta SQL de la respuesta del LLM.
        
        Args:
            response: Respuesta completa del LLM
            
        Returns:
            Consulta SQL extraída
        """
        # Buscar SQL entre bloques de código
        import re
        sql_pattern = r"```sql\s*(.*?)\s*```"
        matches = re.findall(sql_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Si no hay bloques de código, intentar extraer la consulta directamente
        lines = response.strip().split('\n')
        sql_lines = []
        
        for line in lines:
            if line.strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'SHOW')):
                sql_lines.append(line)
                
        if sql_lines:
            return ' '.join(sql_lines)
            
        # Si todo falla, devolver la respuesta completa
        return response.strip()
    
    def explain_query(self, sql_query: str, natural_query: str) -> str:
        """
        Genera una explicación de la consulta SQL.
        
        Args:
            sql_query: Consulta SQL a explicar
            natural_query: Consulta original en lenguaje natural
            
        Returns:
            Explicación de la consulta
        """
        provider = self.provider_manager.get_provider()
        
        prompt = f"""Explica la siguiente consulta SQL de manera sencilla:

SQL: {sql_query}

Esta consulta fue generada para responder a: "{natural_query}"

Proporciona una explicación clara de lo que hace esta consulta SQL y cómo responde a la solicitud original.
"""
        
        explanation = provider.generate_text(prompt)
        return explanation
