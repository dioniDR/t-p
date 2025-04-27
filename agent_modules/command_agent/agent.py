from .task_generator import TaskGenerator
from .task_executor import TaskExecutor
from .command_processor import CommandProcessor

class CommandAgent:
    """
    Agente de comandos que permite procesar entradas de texto 
    y ejecutar tareas usando diferentes proveedores de LLM.
    """
    
    def __init__(self, provider_manager=None, name="CommandAgent"):
        """
        Inicializa el agente de comandos.
        
        Args:
            provider_manager: Gestor de proveedores de LLM (opcional)
            name: Nombre identificativo del agente
        """
        self.name = name
        self.generator = TaskGenerator()
        self.executor = TaskExecutor()
        self.processor = CommandProcessor(provider_manager)
    
    def act(self, input_text):
        """
        Procesa una entrada de texto y ejecuta la acción correspondiente.
        
        Args:
            input_text: Texto de entrada para procesar
            
        Returns:
            Resultado de la acción ejecutada
        """
        # Verificar si es un comando especial
        if self._is_command(input_text):
            return self.processor.process(input_text)
        
        # Procesamiento normal mediante el generador y executor
        task = self.generator.generate(input_text)
        result = self.executor.execute(task)
        return result
    
    def _is_command(self, text):
        """
        Determina si el texto es un comando directo para el processor.
        
        Args:
            text: Texto a analizar
            
        Returns:
            True si el texto es un comando especial, False en caso contrario
        """
        if not text:
            return True
            
        # Lista de comandos que deben ir directamente al processor
        command_prefixes = [
            "usar", "generar", "listar", "ayuda",
            "resumen", "analizar", "traducir", "corregir", "explicar"
        ]
        
        # Verificar si el texto comienza con alguno de los prefijos
        for prefix in command_prefixes:
            if text.lower().startswith(prefix + " ") or text.lower() == prefix:
                return True
                
        return False