import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bd_eclident.db")

def auditar_base_de_datos():
    print("🔍 AUDITORÍA DE LA BASE DE DATOS ECLIDENT 🔍\n")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Revisamos los pacientes
    print("👤 PACIENTES REGISTRADOS:")
    cursor.execute("SELECT num_paciente, nombre, cedula, celular FROM Paciente")
    pacientes = cursor.fetchall()
    if not pacientes:
        print("  (No hay pacientes guardados aún)")
    for p in pacientes:
        print(f"  - ID: {p[0]} | Nombre: {p[1]} | Cédula: {p[2]} | Cel: {p[3]}")
        
    # Revisamos las citas
    print("\n📅 CITAS AGENDADAS:")
    cursor.execute("SELECT id_cita, num_paciente, fecha, hora_inicio, estado FROM Cita")
    citas = cursor.fetchall()
    if not citas:
        print("  (No hay citas guardadas aún)")
    for c in citas:
        print(f"  - Cita ID: {c[0]} | Paciente ID: {c[1]} | Fecha: {c[2]} | Hora: {c[3]} | Estado: {c[4]}")
        
    conexion.close()

if __name__ == "__main__":
    auditar_base_de_datos()