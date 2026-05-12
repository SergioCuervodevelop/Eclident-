import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bd_eclident.db")

def configurar_clinica():
    print("⚙️  Configurando parámetros de la clínica...")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # --- LA MEJORA DEL CEREBRO ---
    # Le agregamos las columnas del sábado a la tabla del Arquitecto
    try:
        cursor.execute("ALTER TABLE Configuracion ADD COLUMN hora_inicio_sabado TEXT")
        cursor.execute("ALTER TABLE Configuracion ADD COLUMN hora_fin_sabado TEXT")
        print("🔧 Se mejoró la base de datos: ¡Columnas de sábado creadas!")
    except sqlite3.OperationalError:
        # Si ya existen, el programa simplemente ignora el error y sigue
        pass

    # 1. Configuramos los horarios de Eclident
    cursor.execute("SELECT COUNT(*) FROM Configuracion")
    if cursor.fetchone()[0] == 0:
        # Insertamos toda la semana normal + el sábado de 8 a 12
        cursor.execute("""
            INSERT INTO Configuracion 
            (buffer_limpieza, hora_inicio_jornada, hora_fin_jornada, hora_inicio_tarde, hora_fin_tarde, hora_inicio_sabado, hora_fin_sabado)
            VALUES (10, '08:00', '12:00', '14:00', '18:00', '08:00', '12:00')
        """)
        print("✅ Horarios configurados: L-V todo el día, Sábados solo en la mañana.")
    else:
        # Si ya habías corrido el script antes, actualizamos la tabla para meter el sábado
        cursor.execute("""
            UPDATE Configuracion 
            SET hora_inicio_sabado = '08:00', 
                hora_fin_sabado = '12:00'
        """)
        print("ℹ️ Horarios actualizados exitosamente con el turno del sábado.")
    
    # 2. Agregamos un Odontólogo de prueba
    cursor.execute("SELECT COUNT(*) FROM Odontologo")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Odontologo (nombre, telefono) VALUES ('Dr. Prueba Eclident', '3000000000')")
        print("✅ Odontólogo de prueba agregado al sistema.")

    conexion.commit()
    conexion.close()
    print("🚀 ¡Todo listo para empezar a agendar!")

if __name__ == "__main__":
    configurar_clinica()