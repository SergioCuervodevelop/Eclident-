from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from .models import UsuarioGoogle


class GoogleSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adaptador personalizado para manejar autenticación con Google"""
    
    def pre_social_login(self, request, sociallogin):
        """Se ejecuta antes de completar el login con Google"""
        # Si el usuario ya existe por email, conectarlo
        if sociallogin.is_existing:
            return
        
        # Verificar si existe un usuario con el mismo email
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
    
    def populate_user(self, request, sociallogin, data):
        """Personalizar datos del usuario cuando se crea"""
        user = super().populate_user(request, sociallogin, data)
        user.first_name = data.get('given_name', '')
        user.last_name = data.get('family_name', '')
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Guardar usuario y crear perfil de Google"""
        user = super().save_user(request, sociallogin, form)
        
        # Crear o actualizar perfil de Google
        extra_data = sociallogin.account.extra_data
        google_profile, created = UsuarioGoogle.objects.get_or_create(
            user=user,
            defaults={
                'google_id': sociallogin.account.uid,
                'nombre_completo': extra_data.get('name', ''),
                'email': user.email,
                'foto': extra_data.get('picture', ''),
            }
        )
        
        # Actualizar si ya existía
        if not created:
            google_profile.nombre_completo = extra_data.get('name', google_profile.nombre_completo)
            google_profile.email = user.email
            google_profile.foto = extra_data.get('picture', google_profile.foto)
            google_profile.save()
        
        return user
