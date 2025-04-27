# Proceso de Liberación de Versiones

## Flujo de Trabajo
1. Desarrollo en rama principal
2. Crear rama de release
3. Pruebas exhaustivas
4. Actualizar documentación
5. Generar changelog
6. Crear tag de versión
7. Publicar en PyPI

## Preparación de Release
```bash
# Crear rama de release
git checkout -b release/vX.Y.Z

# Actualizar versión
# Modificar setup.py o pyproject.toml

# Ejecutar pruebas
pytest
coverage run -m pytest
coverage report

# Generar changelog
gitchangelog
```

## Publicación
```bash
# Crear tag de versión
git tag -a vX.Y.Z -m 'Descripción de la versión'

# Publicar en PyPI
python -m build
python -m twine upload dist/*
```

## Criterios de Release
- Todas las pruebas pasan
- Cobertura de código > 90%
- Documentación actualizada
- Changelog generado
