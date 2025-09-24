# Gobernanza de Datos

## Origen y Linaje
- Todo archivo cargado en **raw** conserva nombre original y fecha de ingesta.
- Cada registro en **bronze** mantiene referencia al archivo y fila de origen.
- En **silver** se conserva el identificador técnico de origen para trazabilidad.

## Validaciones Mínimas
- Fechas: formato válido YYYY-MM-DD y no futuras.
- Partner: no nulo, string limpio (sin caracteres de control).
- Amount: numérico, mayor o igual a 0, en euros.
- Rechazos deben registrarse en logs de validación.

## Política de Mínimos Privilegios
- **Lectura**: todos pueden consultar silver y gold.
- **Escritura**: solo pipelines autorizados.
- **Raw/Bronze**: acceso restringido a ingenieros de datos.
- Sin credenciales incrustadas en código; uso obligatorio de variables de entorno.

## Trazabilidad
- Cada transformación debe ser auditable: de silver a bronze, de bronze a raw.
- Los KPIs deben mostrar % de registros válidos, rechazados y corregidos.
- Documentar reglas de negocio aplicadas en validaciones y transformaciones.

## Roles
- **Ingeniero de datos**: diseña pipelines, controla calidad, administra capas raw/bronze.
- **Analista**: consume datos en silver y gold, interpreta KPIs.
- **Administrador**: gestiona accesos, revisa cumplimiento de gobernanza.

