# Informe de Avances y Próximos Pasos

| | |
|---|---|
| **Proyecto** | BackofficeFixed |
| **Autor** | Luis Mario Suárez |
| **Fecha** | 17 de septiembre de 2026 |
| **Fuente** | `src/backofficefixed/db.py`, `src/backofficefixed/utils/costeo_receta.py` |
| **Complemento** | `docs/INFORME_HALLAZGOS.md` (modelo de datos y reglas de negocio) |

## 1. Avances

### 1.1 Exploración de productos

- Consulta base a `Products` por `Code` (con `IsEnabled = 1`), reutilizada para distintos ejemplos.
- Productos de prueba registrados en el código: `S-014049` (pollo 80 g) y `I-001004` (sal).

### 1.2 Presentaciones del producto

- Se obtienen desde `ProductUnits` por `IdProduct`, con los campos `Id`, `IdProduct`, `IdUnit`, `Items` (gramaje) y `Description`.
- Nota de modelo: `ProductUnits` contiene casi la misma información que las presentaciones y es la tabla que usan los productos de la receta (`RecipeProducts`) para los cálculos, lo que permite saber qué presentación se está usando para el costeo.

### 1.3 Formas de costeo identificadas

Se identificaron dos formas de costear un producto:

1. **Por compra** — costo directo desde `ProductSuppliers`.
2. **Por receta** — suma de los costos de los insumos que componen la receta.

Se decidió trabajar con el **costeo por receta**.

### 1.4 Costeo por receta (implementado en modo exploratorio)

Flujo implementado en `db.py`, solo cuando el producto tiene receta (`Tiene receta? == True`):

1. **Receta principal** — `Recipes` (`Id`, `Code`, `Name`, `IdUnit`) por `Id = Version Receta` y `IsEnabled = 1`, ya que la tabla de recetas es solo una referencia general.
2. **Insumos de la receta** — `RecipeProducts` por `IdRecipeVersion`, con `IdProduct`, `Quantity` e `IdProductUnit`.
3. **Costo de cada insumo** — `ProductSuppliers` por `IdProduct` (campo `Cost`).
4. **Total de la receta** — `total_receta = Σ (Cost × Quantity)`, acumulado con `Decimal`.
5. **Costo por gramaje** — se solicita un gramaje al usuario y se calcula `total_receta × gramaje`.

Hallazgo relevante: `Cost` y `Quantity` ya vienen en formato, por lo que **no es necesario dividir entre 1000**.

### 1.5 Costeo por compra (rama sin receta)

- Cuando el producto no tiene receta, se consulta `ProductSuppliers` (`Id`, `IdProduct`, `IdSupplier`, `Cost`, `IdProductUnit`) para obtener la información de compra y la presentación costeada.

### 1.6 Inicio del refactor

- Se creó la carpeta `utils/` (`utils/__init__.py` vacío).
- `utils/costeo_receta.py` inicia el traslado del costeo a funciones reutilizables:
  - `obtener_receta_producto(idproducto: int)` — actualmente un stub que imprime el id recibido.
  - Importa el cursor con `from db import cursor`, manteniendo el estilo de imports directos del proyecto.

## 2. Qué falta

### 2.1 Costeo

- La lógica de costeo sigue dentro de `db.py` (script de exploración); aún no es reutilizable ni invocable con parámetros.
- `utils/costeo_receta.py` solo contiene un stub.
- El costo por presentación es manual (se pide el gramaje por teclado); falta el cruce automático con `ProductUnits`.
- Reglas de redondeo, precisión y conversión de unidades sin definir.

### 2.2 Transferencias

- `InventoryTransfers` / `InventoryTransfersDetail` aún no se implementan (ni consulta ni actualización).
- Falta definir formalmente el origen de los valores a actualizar (productos, recetas y compras) y el flujo detalle → cabecera.

### 2.3 Robustez y calidad

- La conexión no está controlada: si falla, `conn` no queda definido y los usos posteriores lanzan `NameError`.
- Varias consultas asumen resultados existentes (`fetchone()` puede devolver `None`, por ejemplo si el insumo no tiene proveedor).
- El `input()` de gramaje no valida el valor ingresado.
- Sin tests ni linter/formatter configurados.

### 2.4 Interfaz

- `main.py` sigue vacío; la API con FastAPI/uvicorn está pendiente.

## 3. Qué se puede hacer con los avances

- **Costear un producto con receta** a partir de su `Code`: obtener la receta, sus insumos y el costo total.
- **Obtener las presentaciones** de un producto y el costo de compra de un insumo.
- **Estimar el costo** de una cantidad (gramaje) de la receta o del producto.
- **Costear productos sin receta** por compra.
- Servir como **base directa del refactor**: la lógica ya está validada y solo requiere moverse a funciones.
- Servir como **base para las transferencias**: ya se accede a las tres fuentes necesarias (productos, recetas y compras) para calcular los valores a actualizar.

## 4. Próximo a hacer

| # | Tarea | Prioridad |
|---|---|---|
| 1 | Trasladar el costeo a `utils/costeo_receta.py` como funciones reutilizables (receta, insumos, costo por insumo, total) y dejar `db.py` solo con la conexión. | Alta |
| 2 | Automatizar el costo por presentación usando `ProductUnits` (sin pedir gramaje por teclado). | Alta |
| 3 | Robustecer conexión y consultas: manejo del fallo de conexión, resultados vacíos (`None`) y validación de entradas. | Media |
| 4 | Definir reglas de redondeo, precisión y unidades de costo. | Media |
| 5 | Implementar la consulta y actualización de transferencias (primero detalle, luego cabecera). | Media |
| 6 | Exponer la funcionalidad vía API FastAPI (`main.py`). | Baja |
| 7 | Agregar tests y linter/formatter. | Baja |
