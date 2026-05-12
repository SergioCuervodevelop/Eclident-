import sqlite3
import os

# Apuntamos a tu base de datos que ahora vive dentro de 'inicio/data'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inicio", "data", "bd_eclident.db")

def reparar_codificacion():
    print("⏳ Entrando a la base de datos para corregir ortografía...")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id_servicio, nombre_servicio FROM Servicio")
    servicios = cursor.fetchall()
    
    reparados = 0
    for id_servicio, nombre in servicios:
        try:
            # 🌟 EL TRUCO DE MAGIA: Revertimos el error de lectura a UTF-8 real
            nuevo_nombre = nombre.encode('windows-1252').decode('utf-8')
            
            # Si el nombre cambió (se arregló), lo actualizamos en la tabla
            if nuevo_nombre != nombre:
                cursor.execute("UPDATE Servicio SET nombre_servicio = ? WHERE id_servicio = ?", (nuevo_nombre, id_servicio))
                reparados += 1
        except Exception:
            # Si una palabra ya estaba bien, la dejamos tranquila
            pass
            
    conexion.commit()
    conexion.close()
    print(f"✅ ¡Operación exitosa! Se corrigieron los acentos y eñes de {reparados} tratamientos.")

if __name__ == "__main__":
    reparar_codificacion()