import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bd_eclident.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "servicios.csv")

def migrar_csv_a_bd():
    print("🚀 Activando escáner inteligente de datos...")
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: No encuentro el archivo CSV en {CSV_PATH}")
        return

    try:
        # Leemos el archivo auto-detectando comas o puntos y comas, y SIN saltar filas
        df = pd.read_csv(CSV_PATH, encoding='latin-1', sep=None, engine='python')
        
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        servicios_insertados = 0

        # El radar: Recorremos cada fila y cada celda
        for _, fila in df.iterrows():
            for valor in fila:
                # Si la celda tiene texto y no está vacía
                if pd.notna(valor) and isinstance(valor, str):
                    texto = str(valor).strip()
                    
                    # Filtros del Cerebro para saber si es un tratamiento:
                    # 1. Tiene más de 7 letras
                    # 2. No es un encabezado (como "Descripción" o "Membresia")
                    # 3. No es solo un número con comas (ej. "904,285")
                    if (len(texto) > 7 and 
                        "DESCRIPCI" not in texto.upper() and 
                        "MEMBRESIA" not in texto.upper() and
                        "PARTICULAR" not in texto.upper() and
                        not texto.replace('.', '').replace(',', '').isdigit()):
                        
                        try:
                            # Comprobamos que no hayamos guardado este tratamiento antes
                            cursor.execute("SELECT id_servicio FROM Servicio WHERE nombre_servicio = ?", (texto,))
                            if not cursor.fetchone():
                                # ¡Lo atrapamos! Lo guardamos en SQLite
                                cursor.execute("INSERT INTO Servicio (nombre_servicio, duracion_minutos) VALUES (?, ?)", (texto, 40))
                                servicios_insertados += 1
                                break # Ya encontramos el nombre en esta fila, pasamos a la siguiente
                        except sqlite3.Error:
                            pass

        conexion.commit()
        conexion.close()
        
        print(f"✅ ¡Migración exitosa! El radar encontró e insertó {servicios_insertados} servicios en la base de datos.")
        
    except Exception as e:
        print(f"❌ Ocurrió un error al leer el archivo: {e}")

if __name__ == "__main__":
    migrar_csv_a_bd()