import sqlite3
import os
from modelos import Servicio

# 1. Configuración de la ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bd_eclident.db")

def obtener_catalogo_servicios():
    """
    Se conecta a la base de datos y extrae los servicios
    """
    servicios_listos = []
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No encuentro la base de datos en: {DB_PATH}")
        return []

    try:
        # Nos conectamos a la base de datos
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        # Ejecutamos una consulta SQL para traer la información
        cursor.execute("SELECT id_servicio, nombre_servicio, duracion_minutos FROM Servicio")
        filas = cursor.fetchall()
        
        for fila in filas:
            # Creamos el objeto Servicio.
            # Nota: Como la tabla Servicio no tiene precio, lo dejamos en 0 por ahora
            # y usamos 40 como duración por defecto si no viene en la base de datos.
            nuevo = Servicio(
                id_servicio=fila[0],
                nombre=fila[1],
                duracion_minutos=fila[2] if fila[2] else 40,
                precio_particular=0 
            )
            servicios_listos.append(nuevo)
            
        conexion.close()
        return servicios_listos
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return []

# --- Bloque de prueba interna ---
if __name__ == "__main__":
    print(f"--- Probando conexión a: {DB_PATH} ---")
    servicios = obtener_catalogo_servicios()
    if servicios:
        print(f"✅ ¡Éxito! Se cargaron {len(servicios)} servicios desde la BD.")
        print(f"Primer servicio detectado: {servicios[0].nombre}")
    else:
        print("❌ No se cargaron servicios. La tabla puede estar vacía.")