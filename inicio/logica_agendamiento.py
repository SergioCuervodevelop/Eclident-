import sqlite3
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bd_eclident.db")

# --- 2. FUNCIONES DE CÁLCULO DE TIEMPO ---

def obtener_configuracion():
    """Trae las reglas del juego (horarios) desde SQLite"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT buffer_limpieza, hora_inicio_jornada, hora_fin_jornada, 
               hora_inicio_tarde, hora_fin_tarde, hora_inicio_sabado, hora_fin_sabado
        FROM Configuracion LIMIT 1
    """)
    fila = cursor.fetchone()
    conexion.close()
    
    if fila:
        return {
            "buffer": fila[0],
            "manana_inicio": fila[1],
            "manana_fin": fila[2],
            "tarde_inicio": fila[3],
            "tarde_fin": fila[4],
            "sabado_inicio": fila[5],
            "sabado_fin": fila[6]
        }
    return None

def crear_bloques(hora_inicio_str, hora_fin_str, duracion_servicio, buffer_limpieza):
    """Genera los huecos de tiempo matemáticamente"""
    bloques = []
    formato = "%H:%M"
    
    inicio = datetime.strptime(hora_inicio_str, formato)
    fin = datetime.strptime(hora_fin_str, formato)
    
    tiempo_actual = inicio
    
    while (tiempo_actual + timedelta(minutes=duracion_servicio)) <= fin:
        bloques.append(tiempo_actual.strftime(formato))
        tiempo_actual += timedelta(minutes=(duracion_servicio + buffer_limpieza))
        
    return bloques

def obtener_espacios_dia(fecha_texto, duracion_servicio=40):
    """Calcula todos los espacios TEÓRICOS posibles para un día"""
    config = obtener_configuracion()
    if not config:
        return ["Error: No hay configuración de clínica."]

    fecha_obj = datetime.strptime(fecha_texto, "%Y-%m-%d")
    dia_semana = fecha_obj.weekday() # Lunes=0, ..., Sábado=5, Domingo=6

    espacios_disponibles = []

    if dia_semana == 6:
        return [] # Domingo cerrado

    if dia_semana == 5:
        # Sábado: Solo turno de mañana
        espacios_disponibles.extend(crear_bloques(
            config["sabado_inicio"], config["sabado_fin"], 
            duracion_servicio, config["buffer"]
        ))
    else:
        # Lunes a Viernes: Mañana + Tarde
        espacios_disponibles.extend(crear_bloques(
            config["manana_inicio"], config["manana_fin"], 
            duracion_servicio, config["buffer"]
        ))
        espacios_disponibles.extend(crear_bloques(
            config["tarde_inicio"], config["tarde_fin"], 
            duracion_servicio, config["buffer"]
        ))

    return espacios_disponibles

def filtrar_espacios_ocupados(fecha_texto, id_odontologo, espacios_posibles):
    """Revisa la tabla Cita y quita los horarios que ya están reservados"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT hora_inicio FROM Cita 
        WHERE fecha = ? AND id_odontologo = ? AND estado != 'cancelada'
    """, (fecha_texto, id_odontologo))
    
    citas_ocupadas = [fila[0] for fila in cursor.fetchall()]
    conexion.close()
    
    # Dejamos solo los espacios que NO están en la lista de ocupados
    espacios_libres = [espacio for espacio in espacios_posibles if espacio not in citas_ocupadas]
    
    return espacios_libres

# --- 3. FUNCIONES DE BASE DE DATOS (PACIENTES Y SERVICIOS) ---

def buscar_tratamiento(palabra_clave):
    """Busca en los 181 servicios y devuelve las coincidencias"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    # Buscamos ignorando mayúsculas/minúsculas usando LIKE
    cursor.execute("SELECT id_servicio, nombre_servicio FROM Servicio WHERE nombre_servicio LIKE ?", (f'%{palabra_clave}%',))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def agendar_cita_real(nombre, cedula, direccion, celular, correo, id_servicio, fecha, hora, id_odontologo=1):
    """Guarda al paciente y crea la cita oficial en la base de datos"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        # 1. Verificamos si el paciente ya existe por su cédula
        cursor.execute("SELECT num_paciente FROM Paciente WHERE cedula = ?", (cedula,))
        resultado = cursor.fetchone()
        
        if resultado:
            id_paciente = resultado[0]
            # Si ya existe, actualizamos todos sus datos de contacto
            cursor.execute("""
                UPDATE Paciente 
                SET direccion = ?, celular = ?, correo = ? 
                WHERE num_paciente = ?
            """, (direccion, celular, correo, id_paciente))
        else:
            # Si es nuevo, lo creamos con todos sus datos
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO Paciente (nombre, cedula, direccion, celular, correo, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, cedula, direccion, celular, correo, fecha_hoy))
            id_paciente = cursor.lastrowid 
            
        # 2. Guardamos la cita
        cursor.execute("""
            INSERT INTO Cita (num_paciente, id_servicio, id_odontologo, fecha, hora_inicio, estado)
            VALUES (?, ?, ?, ?, ?, 'pendiente')
        """, (id_paciente, id_servicio, id_odontologo, fecha, hora))
        
        conexion.commit()
        return True, "✅ ¡Cita guardada exitosamente en la base de datos!"
    except Exception as e:
        return False, f"❌ Error al guardar la cita: {e}"
        
    finally:
        conexion.close()

def consultar_agenda_dia(fecha, id_odontologo=1):
    """Busca todas las citas de un día y cruza los datos con Pacientes y Servicios"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        # El comando JOIN une las 3 tablas para darnos un resumen perfecto
        cursor.execute("""
            SELECT C.hora_inicio, P.nombre, P.celular, S.nombre_servicio 
            FROM Cita C
            JOIN Paciente P ON C.num_paciente = P.num_paciente
            JOIN Servicio S ON C.id_servicio = S.id_servicio
            WHERE C.fecha = ? AND C.id_odontologo = ? AND C.estado != 'cancelada'
            ORDER BY C.hora_inicio ASC
        """, (fecha, id_odontologo))
        
        agenda = cursor.fetchall()
        return agenda
    except Exception as e:
        print(f"❌ Error al consultar la agenda: {e}")
        return []
    finally:
        conexion.close()

def obtener_citas_paciente(cedula):
    """Busca todas las citas activas de un paciente usando su cédula"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            SELECT C.id_cita, C.fecha, C.hora_inicio, S.nombre_servicio 
            FROM Cita C
            JOIN Paciente P ON C.num_paciente = P.num_paciente
            JOIN Servicio S ON C.id_servicio = S.id_servicio
            WHERE P.cedula = ? AND C.estado != 'cancelada'
            ORDER BY C.fecha ASC
        """, (cedula,))
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al buscar las citas: {e}")
        return []
    finally:
        conexion.close()

def cancelar_cita(id_cita):
    """Cambia el estado de una cita a 'cancelada' para liberar el espacio"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    try:
        cursor.execute("UPDATE Cita SET estado = 'cancelada' WHERE id_cita = ?", (id_cita,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"❌ Error al cancelar la cita: {e}")
        return False
    finally:
        conexion.close()