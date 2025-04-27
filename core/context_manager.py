# En core/context_manager.py
class ContextManager:
    """Gestiona el contexto de conversación con el usuario."""
    
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history
        self.context_data = {}
    
    def add_message(self, role, content):
        """Añade un mensaje al historial"""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self):
        """Obtiene el contexto completo actual"""
        return {
            "history": self.history,
            "data": self.context_data
        }
    
    def set_context_data(self, key, value):
        """Establece un dato de contexto"""
        self.context_data[key] = value
    
    def clear(self):
        """Limpia el historial y el contexto"""
        self.history = []
        self.context_data = {}