## 3. Configuración (`configuration.md`)

### Archivo de Configuración
- Formato YAML
- Variables de entorno
- Configuración de proveedores

### Estructura Ejemplo
```yaml
default_provider: openai
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
  claude:
    api_key: ${CLAUDE_API_KEY}
```

### Tipos de Configuración
- Credenciales de API
- Modelos por defecto
- Parámetros de generación
- Configuraciones de red