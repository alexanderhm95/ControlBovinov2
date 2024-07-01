from django.utils import timezone
from django.conf import settings
from django.contrib import auth
from datetime import datetime
from django.shortcuts import redirect

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Llama a la vista y obtén la respuesta
        response = self.get_response(request)
        
        # Verifica si la sesión del usuario está activa
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            # Convierte la hora actual a una cadena ISO 8601
            now = timezone.now().isoformat()

            # Si la última actividad registrada es mayor al tiempo de expiración, cierra la sesión
            if last_activity and (datetime.fromisoformat(now) - datetime.fromisoformat(last_activity)).seconds > settings.SESSION_COOKIE_AGE:
                auth.logout(request)
                response.delete_cookie(settings.SESSION_COOKIE_NAME, domain=settings.SESSION_COOKIE_DOMAIN)
                request.session.flush()

                # Eliminar todas las cookies estableciendo su tiempo de expiración en el pasado
                for cookie_name in request.COOKIES:
                    response.delete_cookie(cookie_name)

                # Redirigir al usuario a la página de inicio de sesión
                
                return redirect('login')

            # Actualiza la última actividad en cada solicitud
            request.session['last_activity'] = now

        return response
