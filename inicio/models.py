from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='blog/', null=True, blank=True)

    def __str__(self):
        return self.titulo


class UsuarioGoogle(models.Model):
    """Modelo para guardar datos del usuario autenticado con Google"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_profile')
    google_id = models.CharField(max_length=200, unique=True)
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    foto = models.URLField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre_completo