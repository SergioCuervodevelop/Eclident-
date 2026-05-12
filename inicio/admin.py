from django.contrib import admin
from .models import Post, UsuarioGoogle

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha')
    search_fields = ('titulo', 'contenido')

@admin.register(UsuarioGoogle)
class UsuarioGoogleAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'fecha_registro')
    search_fields = ('nombre_completo', 'email')
    readonly_fields = ('google_id', 'fecha_registro')
