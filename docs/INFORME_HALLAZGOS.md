# Informe de Hallazgos — Modelo de Datos y Reglas de Negocio

| | |
|---|---|
| **Proyecto** | BackofficeFixed |
| **Autor** | Luis Mario Suárez |
| **Fecha** | 17 de septiembre de 2026 |
| **Fuente** | Exploración de la base de datos documentada en `src/backofficefixed/db.py` |
| **Estado** | Hallazgos preliminares |

## 1. Objetivo

Documentar los hallazgos obtenidos durante la exploración de la base de datos del Backoffice, con énfasis en:

- La estructura de la tabla `Products` y el uso de cada uno de sus campos.
- Las reglas de negocio asociadas al costeo de productos con receta.
- El manejo de las transferencias de inventario y su flujo de actualización.

## 2. Alcance

Este informe cubre únicamente lo observado en la exploración inicial registrada en `db.py`. No incluye validaciones con datos productivos ni definiciones funcionales adicionales.

## 3. Tabla `Products`

### 3.1 Consulta de referencia

```sql
select Id,
       Code,
       Name,
       IdProductGroup,
       IdProductSubGroup,
       HasRecipe as 'Tiene receta?',
       IsForSale as 'Se vende?',
       IsProduced as 'Lo hace cedis?',
       IdRecipeVersion as 'Version Receta',
       CalculateRecipeCostOnView as 'Costeo con Receta'
from Products
where code = %s
  and IsEnabled = 1
```

Notas de la consulta:

- La búsqueda se realiza por `Code`.
- El filtro `IsEnabled = 1` restringe el resultado a productos habilitados; un producto deshabilitado se comporta como inexistente.
- Producto de ejemplo utilizado en la exploración: `S-014104` (hamburguesa 90 g).

### 3.2 Campos identificados

| Columna | Alias | Descripción y uso |
|---|---|---|
| `Id` | — | Identificador del producto; se usa para relaciones en la BD. |
| `Code` | — | Código del producto; se usa para búsqueda. |
| `Name` | — | Nombre del producto; se usa para búsqueda. |
| `IdProductGroup` | — | Grupo al que pertenece el producto. |
| `IdProductSubGroup` | — | Subgrupo al que pertenece el producto. |
| `HasRecipe` | Tiene receta? | Indica si el producto se puede costear con la receta. |
| `IsForSale` | Se vende? | Indica si el producto está a la venta. |
| `IsProduced` | Lo hace cedis? | Indica si el producto lo produce CEDIS. Si es así, el costo se obtiene con base en su receta. |
| `IdRecipeVersion` | Versión Receta | Identifica a qué receta pertenece el producto; la tabla de recetas es solo una referencia general. |
| `CalculateRecipeCostOnView` | Costeo con Receta | Indica si el costo del producto se calcula con la receta. |

## 4. Regla de costeo de productos

- Si `HasRecipe` está activo, el producto se puede costear utilizando su receta.
- Si `IsProduced` indica que **lo hace CEDIS**, el costo del producto se obtiene con base en su receta.
- Para ese cálculo se deben obtener las **presentaciones** del producto: las presentaciones son las que contienen el costo.
- Este comportamiento marca la casilla **"Es producto"** en la receta.
- El vínculo con la receta se establece mediante `IdRecipeVersion`, ya que la tabla de recetas funciona como una referencia general y no como el detalle del costeo.

## 5. Transferencias de inventario

### 5.1 Tablas involucradas

| Tabla | Contenido |
|---|---|
| `InventoryTransfers` | Información general de las transferencias. El campo `number` es el folio que da el Backoffice. |
| `InventoryTransfersDetail` | Información de los productos que integran la transferencia, junto con los montos. |

### 5.2 Flujo de actualización de una transferencia

1. Se modifica primero la tabla de detalle (`InventoryTransfersDetail`).
2. Posteriormente se actualizan los valores de `InventoryTransfers` (cabecera).
3. Los valores para actualizar ambas tablas se obtendrán de los **productos**, las **recetas** y las **compras**.

## 6. Puntos abiertos

- Definir con precisión el origen y la fórmula de los valores a actualizar en las transferencias a partir de productos, recetas y compras.
- Confirmar cuáles presentaciones del producto son las que aportan el costo en cada caso.

## 7. Glosario

| Término | Significado |
|---|---|
| CEDIS | Centro de distribución. |
| Presentación | Unidad o empaque del producto; es la entidad que contiene el costo. |
| Folio (`number`) | Número consecutivo asignado por el Backoffice a cada transferencia. |
| Receta | Definición de los insumos y cantidades que componen un producto. |
| Costeo | Cálculo del costo de un producto, directo o a través de su receta. |
| "Es producto" | Casilla de la receta que se marca cuando el producto es elaborado por CEDIS. |
