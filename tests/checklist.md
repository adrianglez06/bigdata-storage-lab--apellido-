
## Checklist de entrega

- [ ] **URL de la app Streamlit funcional**
  - Pegar aquí: "https://w9upodywnlatmejupgtpxx.streamlit.app"
  - La app carga, permite subir CSV y muestra bronze, silver, KPIs y descargas.

- [ ] **bronze.csv y silver.csv subidos a `/data`**
  - `data/bronze/bronze_ventas_mes_2025-05.csv` presentes.
  - `data/silver/silver_ventas_mes_2025-05.csv` presentes.
  - Archivos versionados con nombres auditables.

- [ ] **README con decisiones justificadas (5V → elecciones) y capturas en `docs/`**
  - Justificación clara por Volumen, Velocidad, Variedad, Veracidad, Valor.
  - Capturas de la app y de tablas bronze/silver en `docs/`.

- [ ] **Diccionario y gobernanza completos**
  - `docs/diccionario.md` actualizado con esquema canónico y mapeos.
  - `docs/gobernanza.md` con linaje, validaciones, mínimos privilegios, trazabilidad y roles.


# Rúbrica de evaluación (10 puntos)

## 1) Diseño y justificación — 3 pts
- **3 pts**: Arquitectura clara por capas, decisiones mapeadas a las 5V con trade-offs explícitos. Justifica formatos, schema canónico, particionado temporal y elección de herramientas. Pruebas unitarias básicas presentes.
- **2 pts**: Diseño correcto pero con justificación parcial de las 5V o sin trade-offs. Falta alguna decisión clave documentada.
- **1 pt**: Pipeline funcional sin explicar por qué. Menciona 5V sin conectarlas a decisiones.
- **0 pts**: Diseño confuso, sin capas ni justificación.

## 2) Calidad de datos — 3 pts
- **3 pts**: Validación de tipos y rangos operativa, normalización de importes robusta, fechas ISO, registro de rechazos y KPIs de calidad visibles. Sin NaT en `date`, `amount` numérico estable.
- **2 pts**: Validaciones básicas operan pero faltan KPIs o registro de rechazos. Algún borde sin cubrir.
- **1 pt**: Validaciones incompletas o inestables. Errores frecuentes al subir CSV.
- **0 pts**: Sin validación real. Datos sucios pasan a silver.

## 3) Trazabilidad y modelo DW — 2 pts
- **2 pts**: Linaje completo `source_file` y `ingested_at` en bronze, trazabilidad de silver a bronze reproducible. Agregación por `partner, month` sin duplicados. Estructura DW mínima descrita.
- **1 pt**: Linaje parcial o trazabilidad manual. Alguna ambigüedad en agregaciones.
- **0 pts**: Sin linaje ni posibilidad de rastrear registros.

## 4) Documentación — 2 pts
- **2 pts**: README con instrucciones de despliegue local y en Streamlit Cloud, guía de uso y troubleshooting. Capturas en `docs/`. Diccionario y gobernanza actualizados.
- **1 pt**: Documentación existente pero incompleta o desactualizada.
- **0 pts**: Documentación insuficiente o inexistente.

**Total: 10 puntos**
