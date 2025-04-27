# Estándares de Estilo de Código

## Guías Generales
- Seguir PEP 8
- Máximo 120 caracteres por línea
- Usar snake_case para funciones y variables
- Usar CamelCase para clases

## Ejemplos de Estilo
```python
# Correcto
def calcular_promedio(numeros):
    return sum(numeros) / len(numeros)

# Incorrecto
def calcularPromedio(Numeros):
    return sum(Numeros)/len(Numeros)
```

## Herramientas
- Black para formateo
- Flake8 para linting
- MyPy para tipado

## Configuración
- Usar type hints
- Docstrings para todas las funciones
- Comentarios explicativos
