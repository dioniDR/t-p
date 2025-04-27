# En agent_modules/db_agent/agent.py
from ..base_agent import BaseAgent
from providers.provider_manager import ProviderManager
from .db_connector import DBConnector
from .query_builder import QueryBuilder

class DBAgent(BaseAgent):
    def __init__(self, provider_manager: ProviderManager, **kwargs):
        super().__init__(provider_manager, name="DB Agent")
        self.description = "Agente para consulta de bases de datos mediante lenguaje natural"
        self.connector = DBConnector()
        self.query_builder = QueryBuilder(self.provider_manager)
        self.capabilities = ["query_db", "explain_schema", "suggest_queries"]
        
    def run(self, input_data, **kwargs):
        if not self.validate_input(input_data):
            return {"error": "Input inválido"}
            
        # Determinar intención del usuario
        prompt = input_data.get("prompt", "")
        db_connection = input_data.get("connection", {})
        
        # Construir consulta SQL usando LLM
        sql_query = self.query_builder.build_query(prompt, db_connection)
        
        # Ejecutar consulta
        results = self.connector.execute_query(db_connection, sql_query)
        
        return {
            "query": sql_query,
            "results": results,
            "explanation": self._explain_results(results, prompt)
        }
    
    def get_options(self):
        return [
            {"name": "connection", "type": "dict", "description": "Parámetros de conexión a la base de datos"},
            {"name": "prompt", "type": "string", "description": "Consulta en lenguaje natural"},
        ]
    
    def _explain_results(self, results, original_prompt):
        """Genera una explicación de los resultados usando el proveedor de LLM"""
        provider = self.provider_manager.get_provider()
        explanation_prompt = f"Explica los siguientes resultados de base de datos en relación a la consulta '{original_prompt}':\n{str(results)}"
        return provider.generate_text(explanation_prompt)