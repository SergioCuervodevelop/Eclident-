from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_updated, pre_social_login
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from .models import UsuarioGoogle


@receiver(social_account_updated)
def actualizar_perfil_google(request, socialaccount, **kwargs):
    """Actualizar perfil cuando se autentica con Google"""
    try:
        # Obtener el usuario
        user = socialaccount.user
        
        # Obtener datos de Google
        extra_data = socialaccount.extra_data
        
        # Crear o actualizar UsuarioGoogle
        google_profile, created = UsuarioGoogle.objects.get_or_create(
            user=user,
            defaults={
                'google_id': socialaccount.uid,
                'nombre_completo': extra_data.get('name', ''),
                'email': user.email,
                'foto': extra_data.get('picture', ''),
            }
        )
        
        # Actualizar datos
        if not created:
            google_profile.nombre_completo = extra_data.get('name', google_profile.nombre_completo)
            google_profile.email = user.email
            google_profile.foto = extra_data.get('picture', google_profile.foto)
            google_profile.save()
            
    except Exception as e:
        print(f"Error actualizando perfil de Google: {e}")


@receiver(pre_social_login)
def conectar_usuario_existente(request, socialaccount, **kwargs):
    """Conectar usuario existente con Google"""
    try:
        # Si el email ya existe, conectar la cuenta
        if socialaccount.user.email:
            try:
                user = User.objects.get(email=socialaccount.user.email)
                socialaccount.user = user
            except User.DoesNotExist:
                pass
    except Exception as e:
        print(f"Error conectando usuario: {e}")
