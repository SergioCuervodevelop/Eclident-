"""
URL configuration for eclident_site project.
"""
from inicio import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ¡Agregamos panel_recepcion a la lista de importaciones!
from inicio.views import hola_mundo, vista_agenda, panel_recepcion, login_view, google_login_custom, usuario_perfil

urlpatterns = [
   path('admin/', admin.site.urls),
    path('', hola_mundo, name='inicio'), 
    path('agenda/', vista_agenda, name='agenda'), 
    path('accounts/', include('allauth.urls')),
    path('login/', login_view, name='login'),
    path('google-login/', google_login_custom, name='google_login_custom'),
    path('usuario/', usuario_perfil, name='usuario_perfil'),
    # NUESTRA RUTA SECRETA
    path('recepcion/', panel_recepcion, name='recepcion'), 
    path('blog/', views.blog, name='blog'), 
    path('blog/<int:id>/', views.detalle_post, name='detalle_post'),
    path('contacto/', views.contacto, name='contacto'),
    path('politicas/', views.politicas, name='politicas'),
    path('terminos/', views.terminos, name='terminos'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)