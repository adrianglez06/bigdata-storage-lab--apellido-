# bigdata-storage-lab--gonzalez-

# bigdata-storage-lab-<apellido>

## De CSVs heterogéneos a un almacén analítico confiable

### 1. Objetivo
Construir un pipeline que transforme múltiples fuentes CSV inconsistentes en un almacén analítico estructurado y confiable.  
Secuencia obligatoria:
- **Ingesta**: carga controlada de CSVs heterogéneos.  
- **Validación**: reglas de tipado, rangos, duplicados y consistencia referencial.  
- **Normalización**: estandarización de esquemas, nombres de columnas, tipos y codificación.  
- **Almacenamiento en capas**:  
  - **Bronze**: datos crudos y auditables.  
  - **Silver**: datos limpios y estandarizados.  
- **KPIs**: generación de métricas simples (ej. % filas válidas, % nulos, registros rechazados) como prueba de calidad.

### 2. Entregables
- **Repositorio GitHub público** con:
  - Código del pipeline (ingesta, validación, normalización, carga bronze/silver).  
  - Pruebas unitarias.  
  - Documentación clara en Markdown.  
- **Aplicación Streamlit** mínima que:
  - Permita cargar un CSV de ejemplo.  
  - Visualice el resultado en cada capa (bronze vs silver).  
  - Muestre los KPIs de calidad.  

### 3. Criterios de evaluación
1. **Diseño y justificación**: arquitectura clara, decisiones explicadas en README.  
2. **Calidad de datos**: validaciones implementadas correctamente, rechazos documentados.  
3. **Trazabilidad y modelo DW**: posibilidad de rastrear cualquier registro desde silver hasta su origen bronze.  
4. **Documentación**: instrucciones de despliegue, uso y explicación de KPIs.  

### 4. Qué NO subir
- Datos sensibles, privados o con restricciones legales.  
- CSVs con información personal identificable (PII).  
- Credenciales, contraseñas o tokens.  

### 5. Tiempo estimado por fase
- **Ingesta**: 3 h  
- **Validación**: 4 h  
- **Normalización**: 4 h  
- **Bronze/Silver**: 3 h  
- **KPIs**: 2 h  
- **App Streamlit**: 4 h  
- **Documentación final**: 2 h  
**Total estimado**: 22 h

---
Este laboratorio no es académico: es práctica forzada de ingeniería de datos. Si no respetas la trazabilidad y los controles de calidad, no sirve.  
