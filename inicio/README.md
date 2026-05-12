Eclident - Sistema de Agendamiento Inteligente Web 🪥🦷
Sistema Integral de Gestión Odontológica y Agendamiento Inteligente / An Intelligent Dental Management Scheduling Web System.

Este proyecto ha evolucionado de una herramienta de consola a una Aplicación Web Full-Stack, funcionando como el motor principal para la recepción y atención al paciente de la clínica odontológica Eclident.

🚀 Características Principales
Interfaz Web Intuitiva: Los pacientes pueden agendar sus citas fácilmente desde el navegador web mediante un formulario dinámico que lista todos los tratamientos reales de la clínica.

Panel de Administración Privado: Una sala de control secreta (/recepcion/) donde la recepcionista puede consultar la agenda del día, buscar el historial de los pacientes por cédula y cancelar citas con un solo clic.

Motor Matemático de Agendamiento: Calcula automáticamente los bloques de tiempo disponibles para citas, respetando horarios de apertura y cierre.

Escudos Anti-Errores: Filtros en tiempo real que evitan viajes en el tiempo (citas en el pasado) y el choque de horarios, sugiriendo automáticamente al paciente las horas libres reales.

Migración y Limpieza de Datos: Scripts automatizados para importar el catálogo de precios desde un .csv, insertarlos limpiamente en una base de datos relacional y corregir errores de codificación (acentos y caracteres especiales).

🛠️ Tecnologías Utilizadas
Backend: Python 3.x, Django (Framework Web)

Frontend: HTML5, CSS3, Bootstrap 5 (Diseño Responsivo)

Base de Datos: SQLite3 (Nativa de Python)

Librerías Adicionales: pandas (para la migración inicial de datos).

📂 Estructura del Proyecto
La arquitectura del software sigue el patrón de Django, separando la lógica, el diseño y las configuraciones:

manage.py: El "control remoto" del proyecto para encender el servidor web.

eclident_site/: Configuraciones globales y enrutador principal (urls.py).

inicio/: Aplicación principal de Django.

views.py: El "Chef" que conecta las peticiones de la web con la lógica de Python.

templates/inicio/: Contiene el diseño visual (index.html, agenda.html, recepcion.html).

logica_agendamiento.py: El "Cerebro". Contiene todas las consultas SQL y cálculos de tiempo.

data/: Almacena la base de datos (bd_eclident.db).

limpiar_bd.py: Script cirujano para reparar la ortografía de los tratamientos importados.

⚙️ Instalación y Uso
Para ejecutar este proyecto web en tu máquina local, sigue estos pasos desde la terminal:

Instalar dependencias:

Bash
pip install django pandas
(Opcional) Migración inicial de datos:
Si es la primera vez que se clona el proyecto y la base de datos está vacía:

Bash
python inicio/setup_clinica.py
python inicio/migrar_datos.py
python limpiar_bd.py
Iniciar el servidor web:
Asegúrate de estar en la carpeta raíz (donde está manage.py) y ejecuta:

Bash
python manage.py runserver
Acceder a la plataforma:
Abre tu navegador de internet y visita:

Sitio Público (Pacientes): http://127.0.0.1:8000/

Panel Administrativo (Recepción): http://127.0.0.1:8000/recepcion/

👥 Autores
Karen Ximena Cruz Guzman - Lógica, Backend y Motor de Agendamiento

Johann Sebastian Hernandez - Diseño y Arquitectura de Base de Datos

Sergio Ignacio Cuervo - Diseño Frontend de la página y Estructura Django