from datetime import datetime, timedelta

class Paciente:
    def __init__(self, id_paciente, nombre, cedula, celular, correo):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.cedula = cedula
        self.celular = celular
        self.correo = correo

class Servicio:
    def __init__(self, id_servicio, nombre, duracion_minutos, precio_particular):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.duracion_minutos = duracion_minutos
        self.precio_particular = precio_particular

class Cita:
    def __init__(self, id_cita, paciente, servicio, odontologo, fecha, hora_inicio):
        self.id_cita = id_cita
        self.paciente = paciente  # Aquí guardaremos un objeto de la clase Paciente
        self.servicio = servicio  # Aquí un objeto de la clase Servicio
        self.odontologo = odontologo
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = self.calcular_hora_fin()

    def calcular_hora_fin(self):
        # Convertimos la cadena "08:00" a un objeto de tiempo para sumar
        formato = "%H:%M"
        inicio = datetime.strptime(self.hora_inicio, formato)
        # Sumamos la duración del servicio que viene del objeto Servicio
        fin = inicio + timedelta(minutes=self.servicio.duracion_minutos)
        return fin.strftime(formato)