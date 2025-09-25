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



## Decisiones de arquitectura basadas en las 5V

Este laboratorio prioriza trazabilidad, simplicidad operativa y calidad de datos sobre complejidad innecesaria.

### Volumen
- Alcance: CSVs pequeños y medianos aptos para memoria en Streamlit Cloud (≤ 50 MB por archivo).
- Tecnología: Pandas para ETL en memoria. No se usa Spark ni Dask porque el tamaño objetivo no lo exige.
- Persistencia: capas `data/bronze/` y `data/silver/` versionadas en Git para auditoría. Disco efímero en la nube, repo como verdad de referencia.
- Límite práctico: si un archivo excede memoria, se parte antes de subir o se externaliza a almacenamiento privado. Este laboratorio no cubre particionamiento distribuido.

### Velocidad
- Modo de proceso: batch manual por subida de usuario. Latencia objetivo en segundos.
- Transformaciones vectorizadas y validaciones mínimas para mantener tiempo de respuesta bajo.
- Sin scheduling ni streaming. La frecuencia de carga la marca el usuario.

### Variedad
- Formatos heterogéneos de columnas resueltos con mapeo origen→canónico por archivo.
- Codificaciones soportadas: UTF-8 y latin-1 con lectura de fallback.
- Normalización de importes: limpia símbolo €, elimina miles europeos, convierte coma decimal a punto y soporta negativos entre paréntesis.
- Fechas normalizadas a datetime día y mes derivado como inicio de mes.
- Limpieza de partner: espacios, caracteres de control y blancos a NA.

### Veracidad
- Validaciones mínimas en `basic_checks`: presencia de columnas canónicas, `date` parseable, `amount` numérico, control opcional de `amount ≥ 0`.
- Linaje obligatorio: `source_file` y `ingested_at` UTC en bronze. Silver derivado siempre rastreable a bronze.
- KPIs de calidad: filas totales, nulos, no negativos. Rechazos visibles en la UI.
- Regla operativa: bronze no se edita. Correcciones se aplican en normalización y validación.

### Valor
- Silver agrega `amount` por `partner` y `month` para consumo inmediato en análisis y BI.
- Métricas rápidas: suma mensual, partners activos, ticket medio en gold opcional.
- Descargas reproducibles desde la app para integrarse en flujos aguas abajo.

---


