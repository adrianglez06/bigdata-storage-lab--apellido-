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


## Respuestas a los Prompts de reflexión

1) V dominante hoy y V dominante si 2× tráfico
   - V dominante actual: Veracidad.
   - V dominante con 2× tráfico: Velocidad, con Volumen como segundo factor.
   - Justificación en 3 líneas:
     1. La app ingiere CSV heterogéneos. El mayor riesgo es la calidad y el linaje, no el rendimiento.
     2. Con 2× tráfico, el tiempo de respuesta y la cola de procesamiento impactan la experiencia.
     3. El aumento de filas presiona memoria y E/S. Primero se siente en latencia, luego en tamaño.

2) Trade-off elegido y medición
   - Trade-off concreto elegido: Parquet con compresión Snappy en silver para lectura rápida vs Gzip para máxima compresión.
   - Por qué lo elijo: optimizo tiempo de lectura en la app y en BI. La reducción de CPU en lectura pesa más que ahorrar unos MB.
   - Cómo lo mediré:
     - Métrica 1: tamaño en bytes de silver.csv vs silver.parquet.
     - Métrica 2: tiempo de lectura en ms en 10 repeticiones, mismo dataset y entorno.
     - Diseño del experimento: script reproducible, warmup descartado, media y desviación, commit de resultados en docs/performance.md.

3) Inmutable + linaje y su coste
   - Cómo mejora la veracidad: permite auditar cada registro hasta su archivo fuente y reproducir cualquier agregado sin manipular datos.
   - Qué coste añade: más almacenamiento en bronze, más archivos y complejidad de orquestación y documentación.
   - Decisión operativa resultante: retención definida por mes, nomenclatura con fecha y fuente, cambios solo por nuevas corridas versionadas.

4) KPI principal y SLA del dashboard
   - KPI que gobierna el producto: revenue mensual y partners activos.
   - SLA de actualización: diario 09:00 Europa/Madrid.
   - Decisión que habilita y por qué esa latencia: planificación comercial y seguimiento de ventas. La ingesta es batch diaria y no requiere latencia sub diaria para decisiones de negocio.

5) Riesgo principal del diseño y mitigación
   - Riesgo técnico clave: mapeo incorrecto de columnas que introduce nulos silenciosos y pérdida de registros válidos.
   - Impacto si ocurre: silver infraestima revenue y rompe confianza en el dashboard.
   - Mitigación concreta:
     - Técnica: detección automática de esquema sugerido por similitud de nombres y bloqueo si falta alguna columna canónica.
     - Validación: regla estricta de no nulos en date, partner y amount, duplicados por clave natural rechazados.
     - Operativa: checklist en la app antes de derivar a silver y procedimiento de reingesta con registro de incidentes.
    


| V prioritaria                                | Elecciones (Ingesta/Storage/Compute/Analítica)                                                                                                                 | Riesgos clave                                              | Mitigaciones                                                           | Métrica de éxito                                                                           |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| [Veracidad/Velocidad/Volumen/Variedad/Valor] | Ingesta: [batch o streaming]; Storage: [bronze silver parquet particionado]; Compute: [pandas o Spark, ventanas, dedupe]; Analítica: [KPIs, SLA, segmentación] | [deriva de esquema, datos tardíos, duplicados, PII, picos] | [mapeo dinámico, watermark, clave natural, mascarado PII, autoscaling] | [SLA de frescura, % completitud, tasa de errores, tiempo de lectura, precisión de reporte] |

