# Diccionario de Datos Canónico

## Esquema Canónico

| Campo   | Tipo        | Descripción                                | Ejemplo         |
|---------|-------------|--------------------------------------------|-----------------|
| date    | DATE (YYYY-MM-DD) | Fecha normalizada en formato ISO 8601       | 2025-09-01      |
| partner | STRING      | Nombre de socio/cliente/proveedor           | "ACME Corp"     |
| amount  | FLOAT (EUR) | Monto monetario en euros con decimales      | 1234.56         |

## Mapeos Origen → Canónico

| Origen (columna CSV) | Transformación              | Canónico |
|-----------------------|-----------------------------|----------|
| `fecha`              | Convertir a YYYY-MM-DD      | date     |
| `transaction_date`   | Parsear y normalizar a ISO  | date     |
| `cliente`            | Copiar como string          | partner  |
| `vendor_name`        | Copiar como string          | partner  |
| `importe`            | Convertir a float (EUR)     | amount   |
| `value_usd`          | Convertir a EUR con tipo FX | amount   |

