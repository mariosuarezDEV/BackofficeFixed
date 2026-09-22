from posixpath import curdir

from fastapi import FastAPI, HTTPException

from backofficefixed.db import establecer_conexion

app = FastAPI(title="Backoffice Fixed")


@app.get("/productos/{code}")
def get_producto(code: str):
    conn = establecer_conexion()
    try:
        # Obtener el prducto el producto
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "select Id, Code, Name, IdProductGroup, IdProductSubGroup, HasRecipe as 'Tiene receta?', IsForSale as 'Se vende?', IsProduced as 'Lo hace cedis?', IdRecipeVersion as 'Version Receta', CalculateRecipeCostOnView as 'Costeo con Receta' from Products where code = %s and IsEnabled = 1",
            (code,),
        )
        producto = cursor.fetchone()
        if producto is None:
            return HTTPException(
                status_code=404, detail="El producto no existe o esta deshabilitado"
            )
        return producto
    finally:
        conn.close()


@app.get("/productos/{code}/presentaciones")
def get_presentaciones_producto(code: str):
    conn = establecer_conexion()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "select Id, Code, Name, IdProductGroup, IdProductSubGroup, HasRecipe as 'Tiene receta?', IsForSale as 'Se vende?', IsProduced as 'Lo hace cedis?', IdRecipeVersion as 'Version Receta', CalculateRecipeCostOnView as 'Costeo con Receta' from Products where code = %s and IsEnabled = 1",
            (code,),
        )
        producto = cursor.fetchone()
        if producto is None:
            return HTTPException(
                status_code=404, detail="El producto no existe o esta deshabilitado"
            )
        # Buscar la presentacion
        cursor.execute(
            "select Id, IdProduct, IdUnit, Items as 'GRAMAJE', Description from ProductUnits where IdProduct = %d",
            (producto["Id"],),
        )
        presentaciones = cursor.fetchall()
        if presentaciones is None:
            return HTTPException(
                status_code=404,
                detail=f"No se lograron encontrar las presentaciones del producto {producto['Name']}",
            )
        return presentaciones
    finally:
        conn.close()


@app.get("/productos/{code}/receta")
def get_receta_producto(code: str):
    # Endpoint para obtener la receta de los productos
    conn = establecer_conexion()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "select Id, Code, Name, hasRecipe from Products where Code = %s", (code,)
        )
        producto = cursor.fetchone()
        if producto is None:
            return HTTPException(
                status_code=404, detail="El producto no existe o esta deshabilitado"
            )
        if not producto["hasRecipe"]:
            return HTTPException(
                status_code=404,
                detail=f"El producto {producto['Name']} no tiene receta",
            )
        # Obtener la receta del producto
        cursor.execute(
            "select Id, IdProduct, IdIngredient, Quantity, IdUnit, IdRecipeVersion from RecipeDetails where IdProduct = %d",
            (producto["Id"],),
        )
        receta = cursor.fetchall()
        if receta is None:
            return HTTPException(
                status_code=404,
                detail=f"No se logro encontrar la receta del producto {producto['Name']}",
            )
        return receta

    finally:
        conn.close()


# Obtener costo de un producto
@app.get("/producto/{code}/costo")
def get_producto_costo(code: str):
    conn = establecer_conexion()
    try:
        cursor = conn.cursor()
    finally:
        conn.close()
