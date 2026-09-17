# AGENTS.md

Guía para agentes de IA que trabajen en este repositorio.

## Descripción del proyecto

**BackofficeFixed** es una herramienta en desarrollo cuyo objetivo es consultar y corregir/actualizar información del Backoffice (SQL Server), principalmente:

- Costeo de productos con receta (productos que elabora CEDIS).
- Actualización de transferencias de inventario (`InventoryTransfers` / `InventoryTransfersDetail`).

El detalle del modelo de datos y las reglas de negocio está en `docs/INFORME_HALLAZGOS.md`. El estado de avances y los próximos pasos están en `docs/INFORME_AVANCES.md`.

## Stack

- Python >= 3.14 (ver `.python-version`)
- [uv](https://docs.astral.sh/uv/) para dependencias y entorno (`pyproject.toml`, `uv.lock`, build backend `uv_build`)
- `pymssql` — conexión a SQL Server
- `pandas` — manipulación de resultados
- `python-dotenv` — carga de `.env`
- `fastapi` + `uvicorn` — previstos para una API (aún no implementada)

## Estructura

```
src/backofficefixed/
  __init__.py    # función main() (entry point actual, solo imprime saludo)
  main.py        # vacío — futuro punto de entrada de la API
  schemas.py     # modelos Pydantic (ConexionBD)
  db.py          # conexión a la BD + consultas exploratorias + costeo
  utils/
    __init__.py        # vacío
    costeo_receta.py   # funciones de costeo (en desarrollo; hoy solo un stub)
docs/
  INFORME_HALLAZGOS.md  # hallazgos del modelo de datos y reglas de negocio
  INFORME_AVANCES.md    # avances, pendientes y próximos pasos
```

## Comandos

```powershell
uv sync                      # instalar/actualizar dependencias
uv run backofficefixed       # ejecutar entry point actual
uv run python src/backofficefixed/db.py   # ejecutar consultas exploratorias (requiere .env)
uv run uvicorn <app>         # disponible para la futura API FastAPI
```

## Configuración

`db.py` requiere un archivo `.env` en la raíz (ignorado por git) con estas variables:

| Variable | Descripción |
|---|---|
| `DB_SERVER` | Servidor SQL Server |
| `DB_PORT` | Puerto (default `1433`) |
| `DB_NAME` | Base de datos |
| `DB_USER` | Usuario |
| `DB_PASSWORD` | Contraseña |

Nunca commitear `.env` ni imprimir credenciales en logs o en el código.

## Convenciones y notas importantes

- Los imports internos son directos, sin ruta de paquete: `from schemas import ConexionBD`, `from db import cursor`. Mantener ese estilo.
- `db.py` hoy combina conexión, exploración y costeo (por receta y por compra, con `Decimal`); el refactor en curso mueve el costeo a `utils/costeo_receta.py`.
- Los comentarios y la documentación del dominio están en español; mantener el mismo idioma.
- `db.py` **establece la conexión al ejecutarse** (no está envuelto en funciones). Ejecutarlo abre conexión real a la BD.
- Si la conexión falla, `conn` no queda definido y los usos posteriores lanzan `NameError` (ver `db.py:20-33`).
- `schemas.ConexionBD` usa el campo `passwd` (no `password`).
- `main.py` y `README.md` están vacíos (pendientes).
- No hay tests ni linter/formatter configurados todavía.
- Entorno de desarrollo: Windows + PowerShell.
- Es un repositorio git sin commits iniciales; no commitear salvo que se solicite.

## Glosario de dominio

| Término | Significado |
|---|---|
| CEDIS | Centro de distribución; produce algunos productos. |
| Presentación | Unidad/empaque del producto; contiene el costo. |
| Folio (`InventoryTransfers.number`) | Número asignado por el Backoffice a cada transferencia. |
| Receta | Insumos y cantidades que componen un producto. |
| Costeo con receta | Cálculo del costo usando la receta, marcado por `HasRecipe` / `CalculateRecipeCostOnView`. |
| "Es producto" | Casilla de la receta marcada cuando el producto lo hace CEDIS (`IsProduced`). |
