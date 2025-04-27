## 2. Guía de Proveedores (`providers_guide.md`)

### Crear un Nuevo Proveedor
1. Heredar de `BaseProvider`
2. Implementar método `generate_text()`
3. Manejar autenticación y configuración
4. Seguir interfaz definida

### Ejemplo de Estructura
```python
class NuevoProveedor(BaseProvider):
    def __init__(self, api_key=None):
        # Configuración del proveedor
    
    def generate_text(self, prompt, **kwargs):
        # Lógica de generación de texto
        pass
```

### Requisitos
- Método de autenticación
- Manejo de parámetros de generación
- Gestión de errores
- Configuración flexible