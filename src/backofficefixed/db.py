import os
from decimal import Decimal

import pandas as pd
import pymssql
from dotenv import load_dotenv

from backofficefixed.schemas.schemas import ConexionBD

load_dotenv()

URL_CONN: ConexionBD = ConexionBD(
    server=os.getenv("DB_SERVER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", "1433")),
    user=os.getenv("DB_USER"),
    passwd=os.getenv("DB_PASSWORD"),
)


def establecer_conexion() -> pymssql.Connection:
    try:
        conn = pymssql.connect(
            server=URL_CONN.server,
            port=URL_CONN.port,
            user=URL_CONN.user,
            password=URL_CONN.passwd,
            database=URL_CONN.database,
            charset="UTF-8",
        )
        return conn
    except Exception as E:
        print(f"Error al establecer la conexion con la base de datos:\n{E}")


if __name__ == "__main__":
    conn = establecer_conexion()
    cursor = conn.cursor(as_dict=True)

    # Ejemplo obtener productos de la base de datos

    # S-014049 -> pollo 80gr
    # I-001004 -> Sal

    cursor.execute(
        "select Id, Code, Name, IdProductGroup, IdProductSubGroup, HasRecipe as 'Tiene receta?', IsForSale as 'Se vende?', IsProduced as 'Lo hace cedis?', IdRecipeVersion as 'Version Receta', CalculateRecipeCostOnView as 'Costeo con Receta' from Products where code = %s and IsEnabled = 1",
        ("S-014049",),
    )

    producto = cursor.fetchone()
    columnas_producto = [
        "Id",  # Para relaciones en la BD
        "Code",  # Se usara para busqueda
        "Name",  # Se usara para busqueda
        "IdProductGroup",
        "IdProductSubGroup",
        "Tiene receta?",  # Saber si podemnos costear con la receta
        "Se vende?",
        "Lo hace cedis?",  # Si lo hace cedis entonces sacar el costo del producto con base a su receta (tener que obtener las presentacion del producto, esas presentaciones son las que tendran el costo), esto marca una casilla de 'Es producto' en receta
        "Version Receta",  # Con este sacamos a que receta pertenece ya que la tabla recetas solo es una referencia general
        "Costeo con Receta",
    ]
    if producto is None:
        print("No se encontro el producto o el producto esta deshabilitado")
    else:
        df = pd.DataFrame([producto], columns=columnas_producto)
        print(df)

    # Obtener las presentaciones de un producto
    print("\nPresentaciones del producto\n")
    cursor.execute(
        "select Id, IdProduct, IdUnit, Items as 'GRAMAJE', Description from ProductUnits where IdProduct = %d",
        (producto["Id"],),
    )

    presentaciones = cursor.fetchall()
    columnas_presentaciones = [
        "Id",
        "IdProduct",
        "IdUnit",
        "GRAMAJE",
        "Description",
    ]
    df_presentaciones = pd.DataFrame(presentaciones)
    print(df_presentaciones)

    # Con las presentaciones obtenidas, me gustaria saber el costo de cada una.
    # Formas de costeo: Por compra, Por receta
    # Trabajar con el costo por receta

    # Ejecutar solo si tiene receta
    if producto and producto["Tiene receta?"] == True:
        print("\nInformacion de la receta del producto\n")
        cursor.execute(
            "select Id, Code, Name, IdUnit from Recipes where Id = %d and IsEnabled = 1",
            (producto["Version Receta"]),
        )

        receta_principal = cursor.fetchone()
        df_receta_principal = pd.DataFrame([receta_principal])
        print(df_receta_principal)

        print(f"\nDetalles de la receta {receta_principal['Name']}\n")
        cursor.execute(
            "select Id, IdRecipeVersion, IdProduct, Quantity, IdProductUnit from RecipeProducts where IdRecipeVersion = %d",
            (receta_principal["Id"]),
        )
        productos_receta = cursor.fetchall()
        df_productos_receta = pd.DataFrame(productos_receta)
        print(df_productos_receta)
        # Obtener el costo de cada uno de los productos que aparecen en la receta
        # Para lograrlo, usare el IdProduct de RecipeProducts y los buscare en ProductSuppliers, donde obtendre el "Cost" de la presentacion principal (1kg, 1lt, etc...)
        total_receta: Decimal = Decimal(0)
        for producto_receta in productos_receta:
            cursor.execute(
                "select Cost from ProductSuppliers where IdProduct = %d",
                (producto_receta["IdProduct"]),
            )
            precio = cursor.fetchone()
            # el cost y la cantidad ya estan en formato, ya no es necesario dividir entre 1000
            cuenta = precio["Cost"] * producto_receta["Quantity"]
            total_receta += cuenta
        print(f"\nEl total de la receta es: {total_receta}\n")
        # Saber cuanto cuesta tantos gramos de la receta o del producto, ya es lo mismo para este punto
        gramaje_usuario: Decimal = Decimal(
            input("Ingresa el gramaje a calcular: (X.0-0-0)")
        )
        total_presentacion: Decimal = total_receta * gramaje_usuario
        print(total_presentacion)

    else:  # El producto no tiene receta, entonces veremos su costo
        print(
            "\nEl producto no tiene recetas, voy a obtener la informacion de compra del producto\n"
        )
        # La tabla ProductSuppliers tiene la informacion de el costo y a que unidad esta afectado ese costo (la unidad de se saca de ProductUnits)
        cursor.execute(
            "select Id, IdProduct, IdSupplier, Cost, IdProductUnit as 'ID de Presentacion Costeada' from ProductSuppliers where IdProduct = %d",
            (producto["Id"]),
        )
        costos = cursor.fetchone()
        df_costos = pd.DataFrame([costos])
        print(df_costos)

    # La tabla InventoryTransfers guarda la informacion general de las transferencias, number es el folio que da el backoffice
    # La tabla InventoryTransfersDetail tiene la informacion de los productos junto con los montos
    # Se modifica primero tabla de detalle y luego se actualizan los valores de InventoryTransfers, los valores para actualizar se obtendran de los productos, recetas y compras

    # ProductUnits es una tabla que contiene casi la misma informacion que las presentaciones solo que esta se usa en las recetas de los productos (RecipeProducts) para hacer los calculos, para saber que presentacion se esta usando para el costeo

    cursor.close()
    conn.close()
