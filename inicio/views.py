from datetime import datetime
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import Post, UsuarioGoogle
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
# Importamos todas las funciones necesarias de tu "Cerebro"
from .logica_agendamiento import (
    obtener_espacios_dia, 
    filtrar_espacios_ocupados, 
    buscar_tratamiento, 
    agendar_cita_real, 
    consultar_agenda_dia, 
    obtener_citas_paciente, 
    cancelar_cita,
    completar_cita,
    obtener_datos_paciente,
    obtener_paciente_por_email 
)

def hola_mundo(request):
    """Muestra la página principal (index.html)"""
    return render(request, 'inicio/index.html')

def nosotros(request):
    """Muestra la página de Sobre Nosotros"""
    return render(request, 'inicio/nosotros.html')

def google_login_custom(request):
    """Página de login de Google personalizada con nuestros estilos"""
    return render(request, 'inicio/google_login.html')


def login_view(request):
    """Maneja la página de login y el registro de nuevos usuarios."""
    mensaje = None
    tipo_mensaje = None
    
    if request.method == 'POST':
        # Buscamos qué botón presionó el usuario (login o registro)
        accion = request.POST.get('accion', 'login') # Por defecto asume login
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            mensaje = "❌ Por favor completa todos los campos"
            tipo_mensaje = 'error'
        else:
            # 🟢 CAMINO 1: EL USUARIO SE ESTÁ REGISTRANDO
            if accion == 'registro':
                # Revisamos si el correo ya existe para no duplicarlo
                if User.objects.filter(username=email).exists():
                    mensaje = "❌ Ya existe una cuenta con este correo"
                    tipo_mensaje = 'error'
                else:
                    try:
                        # LA MAGIA: create_user guarda la contraseña encriptada de forma segura
                        nuevo_usuario = User.objects.create_user(
                            username=email, 
                            email=email, 
                            password=password
                        )
                        nuevo_usuario.save()
                        mensaje = "✅ ¡Registro exitoso! Ya puedes iniciar sesión con tu cuenta."
                        tipo_mensaje = 'success'
                    except Exception as e:
                        mensaje = f"❌ Error al crear la cuenta: {str(e)}"
                        tipo_mensaje = 'error'

            # 🔵 CAMINO 2: EL USUARIO ESTÁ INICIANDO SESIÓN (Tu código original)
            elif accion == 'login':
                try:
                    user = authenticate(request, username=email, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('usuario_perfil')
                    else:
                        mensaje = "❌ Email o contraseña incorrectos"
                        tipo_mensaje = 'error'
                except Exception as e:
                    mensaje = f"❌ Error al iniciar sesión: {str(e)}"
                    tipo_mensaje = 'error'

    return render(request, 'inicio/Login.html', {'mensaje': mensaje, 'tipo_mensaje': tipo_mensaje})


def recuperar_contrasena(request):
    """Maneja la recuperación y cambio de contraseña"""
    mensaje = None
    tipo_mensaje = None
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'buscar':
            email = request.POST.get('email')
            
            try:
                user = User.objects.get(email=email)
                # Guardar el email en sesión para el siguiente paso
                request.session['recover_email'] = email
                request.session['recover_user_id'] = user.id
                mensaje = f"✅ Cuenta encontrada. Establece tu nueva contraseña"
                tipo_mensaje = 'success'
            except User.DoesNotExist:
                mensaje = "❌ No hay una cuenta registrada con ese email"
                tipo_mensaje = 'error'
        
        elif accion == 'cambiar':
            email = request.session.get('recover_email')
            contraseña_nueva = request.POST.get('contraseña_nueva')
            contraseña_confirmacion = request.POST.get('contraseña_confirmacion')
            
            # Validaciones
            if not email:
                mensaje = "❌ Debes buscar tu cuenta primero"
                tipo_mensaje = 'error'
            elif not contraseña_nueva or not contraseña_confirmacion:
                mensaje = "❌ Por favor completa todos los campos"
                tipo_mensaje = 'error'
            elif contraseña_nueva != contraseña_confirmacion:
                mensaje = "❌ Las contraseñas no coinciden"
                tipo_mensaje = 'error'
            elif len(contraseña_nueva) < 8:
                mensaje = "❌ La contraseña debe tener al menos 8 caracteres"
                tipo_mensaje = 'error'
            else:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(contraseña_nueva)
                    user.save()
                    # Limpiar sesión
                    if 'recover_email' in request.session:
                        del request.session['recover_email']
                    if 'recover_user_id' in request.session:
                        del request.session['recover_user_id']
                    mensaje = "✅ Contraseña actualizada exitosamente. Ya puedes iniciar sesión"
                    tipo_mensaje = 'success'
                    # Mostrar formulario de login después de 2 segundos
                    return render(request, 'inicio/recuperar_contrasena.html', {
                        'mensaje': mensaje,
                        'tipo_mensaje': tipo_mensaje,
                        'mostrar_login': True
                    })
                except Exception as e:
                    mensaje = f"❌ Error al cambiar contraseña: {str(e)}"
                    tipo_mensaje = 'error'
    
    # Verificar si el email ya fue buscado
    email_encontrado = request.session.get('recover_email')
    
    contexto = {
        'mensaje': mensaje,
        'tipo_mensaje': tipo_mensaje,
        'email_encontrado': email_encontrado,
    }
    
    return render(request, 'inicio/recuperar_contrasena.html', contexto)

@login_required(login_url='login')
def vista_agenda(request):
    """
    Maneja la lógica de agendamiento inteligente.
    - Autocompleta datos desde el perfil de Google o historial clínico.
    - Valida disponibilidad de horarios dinámicamente.
    - Protege contra citas en fechas pasadas.
    """
    mensaje = None
    exito = False
    datos_previos_clinica = None
    google_profile = None

    # 1. RECUPERACIÓN DE DATOS (Para autocompletar el formulario)
    if request.user.is_authenticated:
        # Buscamos si el correo ya tiene historial registrado en la clínica (Cédula, Celular, Dirección)
        datos_previos_clinica = obtener_paciente_por_email(request.user.email)
        
        # Intentamos obtener el perfil de Google para el nombre completo
        try:
            google_profile = request.user.google_profile
        except Exception:
            google_profile = None

    # Cargamos siempre la lista de tratamientos para el selector
    todos_los_tratamientos = buscar_tratamiento("")

    # 2. PROCESAMIENTO DEL FORMULARIO (Cuando el usuario hace clic en Confirmar)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cedula = request.POST.get('cedula')
        direccion = request.POST.get('direccion')
        celular = request.POST.get('celular')
        correo = request.POST.get('correo')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        id_servicio = request.POST.get('tratamiento_id')

        # A. Validación: No permitir fechas pasadas
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha_obj < datetime.now().date():
                mensaje = "❌ Error: No puedes agendar citas en fechas que ya pasaron."
                return render(request, 'inicio/agenda.html', {
                    'mensaje': mensaje, 
                    'exito': False,
                    'tratamientos': todos_los_tratamientos,
                    'datos_previos': datos_previos_clinica,
                    'google_profile': google_profile
                })
        except (ValueError, TypeError):
            pass

        # B. Validación: Verificar disponibilidad real del horario seleccionado
        espacios_teoricos = obtener_espacios_dia(fecha)
        if not espacios_teoricos or "Error" in espacios_teoricos[0]:
            mensaje = "❌ El día seleccionado no está disponible o la clínica se encuentra cerrada."
        else:
            # Filtramos los espacios que realmente están libres en la base de datos
            espacios_reales = filtrar_espacios_ocupados(fecha, 1, espacios_teoricos)
            
            if hora not in espacios_reales:
                mensaje = f"⚠️ La hora {hora} se acaba de ocupar. Por favor, selecciona una de las horas disponibles."
            else:
                # C. Guardado Oficial: Registramos la cita en el sistema
                exito_agenda, msj_agenda = agendar_cita_real(
                    nombre, cedula, direccion, celular, correo, id_servicio, fecha, hora, 1
                )
                mensaje = msj_agenda
                exito = exito_agenda

    # 3. RENDERIZADO FINAL
    return render(request, 'inicio/agenda.html', {
        'mensaje': mensaje, 
        'exito': exito,
        'tratamientos': todos_los_tratamientos,
        'datos_previos': datos_previos_clinica, # Datos de la clínica (Cédula, Tel, Dir)
        'google_profile': google_profile      # Datos de Google (Nombre completo)
    })

@staff_member_required(login_url='inicio')
def panel_recepcion(request):
    """Panel de control administrativo para la recepcionista"""
    agenda = None
    citas_paciente = None
    datos_paciente = None
    mensaje = None

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # Acción: Ver todas las citas de una fecha específica
        if accion == 'ver_agenda':
            fecha = request.POST.get('fecha_agenda')
            agenda = consultar_agenda_dia(fecha, 1)
            if not agenda:
                mensaje = f"✅ La agenda está libre. No hay citas para el {fecha}."

        # Acción: Buscar paciente por cédula (trae datos personales e historial)
        elif accion == 'buscar_paciente':
            cedula = request.POST.get('cedula_buscar')
            datos_paciente = obtener_datos_paciente(cedula)
            citas_paciente = obtener_citas_paciente(cedula)
            
            if not datos_paciente:
                mensaje = f"⚠️ No se encontró ningún paciente con la cédula {cedula}."

        # Acción: Cancelar una cita específica por su ID
        elif accion == 'cancelar_cita':
            id_cita = request.POST.get('id_cita_cancelar')
            if cancelar_cita(id_cita):
                mensaje = f"🗑️ ¡Cita #{id_cita} cancelada exitosamente!"
            else:
                mensaje = f"❌ Error al intentar cancelar la cita #{id_cita}."

        # Acción: Marcar una cita como completada (Asistencia)
        elif accion == 'completar_cita':
            id_cita = request.POST.get('id_cita_completar')
            if completar_cita(id_cita):
                mensaje = f"✅ Cita #{id_cita} marcada como COMPLETADA exitosamente."
            else:
                mensaje = f"❌ Error al intentar completar la cita #{id_cita}."

    return render(request, 'inicio/recepcion.html', {
        'agenda': agenda,
        'citas_paciente': citas_paciente,
        'datos_paciente': datos_paciente,
        'mensaje': mensaje
    })
    
def blog(request):
    """Lista todas las publicaciones del blog"""
    posts = Post.objects.all().order_by('-fecha')
    return render(request, 'inicio/blog.html', {'posts': posts})

def detalle_post(request, id):
    """Muestra el contenido completo de un post del blog"""
    post = get_object_or_404(Post, id=id)
    return render(request, 'inicio/detalle_post.html', {'post': post})

def contacto(request):
    """Muestra la página de contacto"""
    return render(request, 'inicio/contacto.html')

def politicas(request):
    """Muestra la página de políticas de privacidad"""
    return render(request, 'inicio/politicas.html')

def terminos(request):
    """Muestra la página de términos y condiciones"""
    return render(request, 'inicio/terminos.html')


def logout_view(request):
    """Cierra sesión del usuario y redirige a inicio"""
    logout(request)
    return redirect('inicio')


@login_required(login_url='login')
def usuario_perfil(request):
    """Muestra el perfil del paciente autenticado con datos de Google"""
    usuario = request.user
    google_profile = None
    try:
        google_profile = usuario.google_profile
    except UsuarioGoogle.DoesNotExist:
        pass
    
    # Obtener historial si el usuario está registrado como paciente
    citas = consultar_agenda_dia(None, 1) if hasattr(usuario, 'cedula') else []
    
    contexto = {
        'usuario': usuario,
        'google_profile': google_profile,
        'citas': citas,
    }


    return render(request, 'inicio/Usuario.html', contexto)
def api_horas_disponibles(request):
    """Mini-API que devuelve las horas libres cuando el paciente elige una fecha"""
    fecha = request.GET.get('fecha')
    if not fecha:
        return JsonResponse({'horas': []})

    # Usamos tu cerebro de agendamiento
    espacios_teoricos = obtener_espacios_dia(fecha)
    if not espacios_teoricos or "Error" in espacios_teoricos[0]:
        return JsonResponse({'horas': []})

    espacios_reales = filtrar_espacios_ocupados(fecha, 1, espacios_teoricos)
    return JsonResponse({'horas': espacios_reales})