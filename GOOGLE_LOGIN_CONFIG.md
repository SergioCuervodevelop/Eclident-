# Configuración de Google Sign-In SDK

## Pasos para obtener tu Google Client ID:

1. **Ve a [Google Cloud Console](https://console.cloud.google.com/)**
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ 
4. Ve a "Credenciales" 
5. Crea una nueva credencial OAuth 2.0 de tipo "ID de cliente de web"
6. En URIs autorizados de JavaScript, agrega:
   - `http://localhost:8000` (desarrollo)
   - `https://tudominio.com` (producción)
7. En URIs de redirección autorizadas, agrega:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://tudominio.com/accounts/google/login/callback/`

## Pasos para configurar en tu proyecto:

### 1. Reemplaza el Client ID en Login.html
En el archivo `inicio/templates/inicio/Login.html`, reemplaza `TU_GOOGLE_CLIENT_ID` en DOS lugares:

**Línea ~48:**
```html
data-client_id="TU_GOOGLE_CLIENT_ID"
```

**Línea ~74:**
```javascript
client_id: 'TU_GOOGLE_CLIENT_ID',
```

### 2. Configura django-allauth en settings.py

Asegúrate de que en `eclident_site/settings.py` tengas:

```python
# Social account settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'INIT_PARAMS': {
            'display': 'popup',
        },
        'FIELDS': [
            'id',
            'email',
            'name',
            'picture',
            'locale'
        ]
    }
}

# Redirigir después del login
LOGIN_REDIRECT_URL = '/recepcion/'  # Cambiar según tus necesidades
SOCIALACCOUNT_AUTO_SIGNUP = True
```

### 3. Ventajas de esta solución:

✅ El popup de Google aparece **dentro de tu página**
✅ Se mantienen **todos tus estilos personalizados**
✅ No hay redirección a Google
✅ Integración completa con **django-allauth**
✅ Mejor experiencia de usuario

### 4. Notas importantes:

- El usuario verá el popup de Google dentro de tu página con tu fondo y estilos
- Si el login es exitoso, se redirige automáticamente al destino configurado en `LOGIN_REDIRECT_URL`
- Si el usuario cancela, simplemente cierra el popup y puede intentar de nuevo
