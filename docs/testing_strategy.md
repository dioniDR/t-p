# Estrategia de Testing

## Tipos de Pruebas
- Unitarias
- Integración
- Funcionales
- Cobertura

## Frameworks
- pytest para pruebas unitarias
- coverage.py para cobertura

## Ejecución de Pruebas
```bash
# Correr todas las pruebas
pytest tests/

# Cobertura de código
coverage run -m pytest
coverage report
```

## Criterios de Pruebas
- 90%+ de cobertura de código
- Pruebas para cada proveedor
- Pruebas de integración
- Manejo de casos de error
